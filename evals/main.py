#!/usr/bin/env python3
"""Command-line interface for running evaluations."""

import argparse
import asyncio
import os
import sys
from typing import (
    Any,
    Dict,
    Optional,
)

import colorama
from colorama import (
    Fore,
    Style,
)

# Fix import path for app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings
from app.core.logging import logger
from evals.evaluator import Evaluator

# Default configuration
DEFAULT_CONFIG = {
    "generate_report": True,
    "model": settings.EVALUATION_LLM,
    "api_base": settings.EVALUATION_BASE_URL,
}


def print_title(title: str) -> None:
    """Print a formatted title with colors.

    Args:
        title: The title text to print
    """
    print("\n" + "=" * 60)
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(60)}{Style.RESET_ALL}")
    print("=" * 60 + "\n")


def print_info(message: str) -> None:
    """Print an info message with colors.

    Args:
        message: The message to print
    """
    print(f"{Fore.GREEN}• {message}{Style.RESET_ALL}")


def print_warning(message: str) -> None:
    """Print a warning message with colors.

    Args:
        message: The message to print
    """
    print(f"{Fore.YELLOW}⚠ {message}{Style.RESET_ALL}")


def print_error(message: str) -> None:
    """Print an error message with colors.

    Args:
        message: The message to print
    """
    print(f"{Fore.RED}✗ {message}{Style.RESET_ALL}")


def print_success(message: str) -> None:
    """Print a success message with colors.

    Args:
        message: The message to print
    """
    print(f"{Fore.GREEN}✓ {message}{Style.RESET_ALL}")


def get_user_input(prompt: str, default: Optional[str] = None) -> Optional[str]:
    """Get user input with a colored prompt.

    Args:
        prompt: The prompt to display
        default: Default value if user presses enter

    Returns:
        User input or default value (which may be None if no default was supplied)
    """
    default_text = f" [{default}]" if default else ""
    user_input = input(f"{Fore.BLUE}{prompt}{default_text}: {Style.RESET_ALL}")
    return user_input if user_input else default


def get_yes_no(prompt: str, default: bool = True) -> bool:
    """Get a yes/no response from the user.

    Args:
        prompt: The prompt to display
        default: Default value if user presses enter

    Returns:
        True for yes, False for no
    """
    default_value = "Y/n" if default else "y/N"
    response = get_user_input(f"{prompt} {default_value}")

    if not response:
        return default

    return response.lower() in ("y", "yes")


def display_summary(report: Dict[str, Any]) -> None:
    """Display a summary of the evaluation results.

    Args:
        report: The evaluation report
    """
    print_title("Evaluation Summary")

    print(f"{Fore.CYAN}Model:{Style.RESET_ALL} {report['model']}")
    print(f"{Fore.CYAN}Duration:{Style.RESET_ALL} {report['duration_seconds']} seconds")
    print(f"{Fore.CYAN}Total Traces:{Style.RESET_ALL} {report['total_traces']}")

    success_rate = 0
    if report["total_traces"] > 0:
        success_rate = (report["successful_traces"] / report["total_traces"]) * 100

    if success_rate > 80:
        status_color = Fore.GREEN
    elif success_rate > 50:
        status_color = Fore.YELLOW
    else:
        status_color = Fore.RED

    print(
        f"{Fore.CYAN}Success Rate:{Style.RESET_ALL} {status_color}{success_rate:.1f}%{Style.RESET_ALL} ({report['successful_traces']}/{report['total_traces']})"
    )

    print("\n" + f"{Fore.CYAN}Metrics Summary:{Style.RESET_ALL}")
    for metric_name, data in report["metrics_summary"].items():
        total = data["success_count"] + data["failure_count"]
        success_percent = 0
        if total > 0:
            success_percent = (data["success_count"] / total) * 100

        if success_percent > 80:
            status_color = Fore.GREEN
        elif success_percent > 50:
            status_color = Fore.YELLOW
        else:
            status_color = Fore.RED

        print(
            f"  • {metric_name}: {status_color}{success_percent:.1f}%{Style.RESET_ALL} success, avg score: {data['avg_score']:.2f}"
        )

    if report["generate_report_path"]:
        print(f"\n{Fore.CYAN}Report generated at:{Style.RESET_ALL} {report['generate_report_path']}")


async def run_evaluation(generate_report: bool = True) -> None:
    """Run the evaluation process.

    Args:
        generate_report: Whether to generate a JSON report
    """
    print_title("Starting Evaluation")
    print_info(f"Using model: {settings.EVALUATION_LLM}")
    print_info(f"Report generation: {'Enabled' if generate_report else 'Disabled'}")

    try:
        evaluator = Evaluator()
        await evaluator.run(generate_report_file=generate_report)

        print_success("Evaluation completed successfully!")

        # Display summary of results
        display_summary(evaluator.report)

    except Exception as e:
        print_error(f"Evaluation failed: {str(e)}")
        logger.error("evaluation_failed", error=str(e))
        sys.exit(1)


def display_configuration(config: Dict[str, Any]) -> None:
    """Display the current configuration.

    Args:
        config: The configuration dictionary
    """
    print_title("Configuration")
    print_info(f"Model: {config['model']}")
    print_info(f"API Base: {config['api_base']}")
    print_info(f"Generate Report: {'Yes' if config['generate_report'] else 'No'}")


def interactive_mode() -> None:
    """Run the evaluator in interactive mode."""
    colorama.init()

    # Create a configuration with default values
    config = DEFAULT_CONFIG.copy()

    print_title("Evaluation Runner")
    print_info("Welcome to the Evaluation Runner!")
    print_info("Press Enter to accept default values or input your own.")

    # Display current configuration
    display_configuration(config)

    print("\n" + f"{Fore.CYAN}Configuration Options (press Enter to accept defaults):{Style.RESET_ALL}")

    # Allow user to change configuration or accept defaults
    change_config = get_yes_no("Would you like to change the default configuration?", default=False)

    if change_config:
        config["generate_report"] = get_yes_no("Generate JSON report?", default=config["generate_report"])

    print("\n")
    confirm = get_yes_no("Ready to start evaluation with these settings?", default=True)

    if confirm:
        asyncio.run(run_evaluation(generate_report=config["generate_report"]))
    else:
        print_warning("Evaluation canceled.")


def quick_mode() -> None:
    """Run the evaluator with all default settings."""
    colorama.init()
    print_title("Quick Evaluation")
    print_info("Running evaluation with default settings...")
    print_info("(Press Ctrl+C to cancel)")

    # Display defaults
    display_configuration(DEFAULT_CONFIG)

    try:
        asyncio.run(run_evaluation(generate_report=DEFAULT_CONFIG["generate_report"]))
    except KeyboardInterrupt:
        print_warning("\nEvaluation canceled by user.")
        sys.exit(0)


def main() -> None:
    """Main entry point for the command-line interface."""
    parser = argparse.ArgumentParser(description="Run evaluations on model outputs")
    parser.add_argument("--no-report", action="store_true", help="Don't generate a JSON report")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    parser.add_argument("--quick", action="store_true", help="Run with all default settings (no prompts)")

    args = parser.parse_args()

    if args.quick:
        quick_mode()
    elif args.interactive:
        interactive_mode()
    else:
        # Run with command-line arguments
        asyncio.run(run_evaluation(generate_report=not args.no_report))


if __name__ == "__main__":
    main()
