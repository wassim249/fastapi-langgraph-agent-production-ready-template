"""Evaluator for evals."""

import os
import sys
import time
from datetime import (
    datetime,
    timedelta,
)
from time import sleep

import openai
from langfuse import Langfuse
from langfuse.api.resources.commons.types.trace_with_details import TraceWithDetails
from tqdm import tqdm

# Fix import path for app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings
from app.core.logging import logger
from evals.helpers import (
    calculate_avg_scores,
    generate_report,
    get_input_output,
    initialize_metrics_summary,
    initialize_report,
    process_trace_results,
    update_failure_metrics,
    update_success_metrics,
)
from evals.metrics import metrics
from evals.schemas import ScoreSchema


class Evaluator:
    """Evaluates model outputs using predefined metrics.

    This class handles fetching traces from Langfuse, evaluating them against
    metrics, and uploading scores back to Langfuse.

    Attributes:
        client: OpenAI client for API calls.
        langfuse: Langfuse client for trace management.
    """

    def __init__(self):
        """Initialize Evaluator with OpenAI and Langfuse clients."""
        self.client = openai.AsyncOpenAI(api_key=settings.EVALUATION_API_KEY, base_url=settings.EVALUATION_BASE_URL)
        self.langfuse = Langfuse(
            public_key=settings.LANGFUSE_PUBLIC_KEY,
            secret_key=settings.LANGFUSE_SECRET_KEY,
            timeout=60,  # In seconds
        )
        # Initialize report data structure
        self.report = initialize_report(settings.EVALUATION_LLM)
        initialize_metrics_summary(self.report, metrics)

    async def run(self, generate_report_file=True):
        """Main execution function that fetches and evaluates traces.

        Retrieves traces from Langfuse, evaluates each one against all metrics,
        and uploads the scores back to Langfuse.

        Args:
            generate_report_file: Whether to generate a JSON report after evaluation. Defaults to True.
        """
        start_time = time.time()
        traces = self.__fetch_traces()
        self.report["total_traces"] = len(traces)

        trace_results = {}

        for trace in tqdm(traces, desc="Evaluating traces"):
            trace_id = trace.id
            trace_results[trace_id] = {
                "success": False,
                "metrics_evaluated": 0,
                "metrics_succeeded": 0,
                "metrics_results": {},
            }

            for metric in tqdm(metrics, desc=f"Applying metrics to trace {trace_id[:8]}...", leave=False):
                metric_name = metric["name"]
                input, output = get_input_output(trace)
                if input is None or output is None:
                    update_failure_metrics(self.report, trace_id, metric_name, trace_results)
                    trace_results[trace_id]["metrics_evaluated"] += 1
                    continue
                score = await self._run_metric_evaluation(metric, input, output)

                if score:
                    self._push_to_langfuse(trace, score, metric)
                    update_success_metrics(self.report, trace_id, metric_name, score, trace_results)
                else:
                    update_failure_metrics(self.report, trace_id, metric_name, trace_results)

                trace_results[trace_id]["metrics_evaluated"] += 1

            process_trace_results(self.report, trace_id, trace_results, len(metrics))
            sleep(settings.EVALUATION_SLEEP_TIME)

        self.report["duration_seconds"] = round(time.time() - start_time, 2)
        calculate_avg_scores(self.report)

        if generate_report_file:
            generate_report(self.report)

        logger.info(
            "evaluation_completed",
            total_traces=self.report["total_traces"],
            successful_traces=self.report["successful_traces"],
            failed_traces=self.report["failed_traces"],
            duration_seconds=self.report["duration_seconds"],
        )

    def _push_to_langfuse(self, trace: TraceWithDetails, score: ScoreSchema, metric: dict):
        """Push evaluation score to Langfuse.

        Args:
            trace: The trace to score.
            score: The evaluation score.
            metric: The metric used for evaluation.
        """
        self.langfuse.create_score(
            trace_id=trace.id,
            name=metric["name"],
            data_type="NUMERIC",
            value=score.score,
            comment=score.reasoning,
        )

    async def _run_metric_evaluation(self, metric: dict, input: str, output: str) -> ScoreSchema | None:
        """Evaluate a single trace against a specific metric.

        Args:
            metric: The metric definition to use for evaluation.
            input: The input to evaluate.
            output: The output to evaluate.

        Returns:
            ScoreSchema with evaluation results or None if evaluation failed.
        """
        metric_name = metric["name"]
        if not metric:
            logger.error("metric_not_found", metric_name=metric_name)
            return None
        system_metric_prompt = metric["prompt"]

        if not input or not output:
            logger.error(
                "metric_evaluation_failed_missing_io",
                metric_name=metric_name,
                has_input=bool(input),
                has_output=bool(output),
            )
            return None
        score = await self._call_openai(system_metric_prompt, input, output)
        if score:
            logger.info(
                "metric_evaluation_completed",
                metric_name=metric_name,
                score=score.score,
                reasoning=score.reasoning,
            )
        else:
            logger.error("metric_evaluation_failed", metric_name=metric_name)
        return score

    async def _call_openai(self, metric_system_prompt: str, input: str, output: str) -> ScoreSchema | None:
        """Call OpenAI API to evaluate a trace.

        Args:
            metric_system_prompt: System prompt defining the evaluation metric.
            input: Formatted input messages.
            output: Formatted output message.

        Returns:
            ScoreSchema with evaluation results or None if API call failed.
        """
        num_retries = 3
        for _ in range(num_retries):
            try:
                response = await self.client.beta.chat.completions.parse(
                    model=settings.EVALUATION_LLM,
                    messages=[
                        {"role": "system", "content": metric_system_prompt},
                        {"role": "user", "content": f"Input: {input}\nGeneration: {output}"},
                    ],
                    response_format=ScoreSchema,
                )
                return response.choices[0].message.parsed
            except Exception as e:
                SLEEP_TIME = 10
                logger.error(
                    "openai_evaluation_call_failed",
                    error=str(e),
                    sleep_seconds=SLEEP_TIME,
                )
                sleep(SLEEP_TIME)
                continue
        return None

    def __fetch_traces(self) -> list[TraceWithDetails]:
        """Fetch traces from the past 24 hours without scores.

        Returns:
            List of traces that haven't been scored yet.
        """
        last_24_hours = datetime.now() - timedelta(hours=24)
        logger.info("fetching_langfuse_traces", from_timestamp=str(last_24_hours))
        try:
            traces = self.langfuse.api.trace.list(
                from_timestamp=last_24_hours, order_by="timestamp.asc", limit=100
            ).data
            traces_without_scores = [trace for trace in traces if not trace.scores]
            return traces_without_scores
        except Exception as e:
            logger.error("langfuse_traces_fetch_failed", error=str(e))
            return []
