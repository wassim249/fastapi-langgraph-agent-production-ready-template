"""LiveKit Agents executor for inbound phone calls using Gemini Live (speech-to-speech)."""

from __future__ import annotations

from livekit.agents import (
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    cli,
    metrics,
    room_io,
)
from livekit.plugins import (
    google,
    silero,
)

from app.core.config import settings
from app.core.langgraph.phone_agent.agent import create_phone_agent
from app.core.logging import logger


def _prewarm(proc: JobProcess) -> None:
    proc.userdata["vad"] = silero.VAD.load()
    logger.info("phone_agent_prewarm_completed")


def _build_session(*, vad: object) -> AgentSession:
    return AgentSession(
        vad=vad,
        # Gemini Live: speech-to-speech realtime model (handles STT + LLM + TTS internally)
        llm=google.realtime.RealtimeModel(
            voice=settings.LIVEKIT_PHONE_AGENT_VOICE,
        ),
    )


def _build_room_options() -> room_io.RoomOptions:
    return room_io.RoomOptions(
        audio_input=room_io.AudioInputOptions(
            # Keep defaults; placeholder for phone-quality processing options.
        ),
    )


def _bind_metrics_handlers(
    *,
    session: AgentSession,
    usage_collector: metrics.UsageCollector,
) -> None:
    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent) -> None:
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)


def _register_entrypoint(server: AgentServer) -> None:
    if settings.LIVEKIT_PHONE_AGENT_EXPLICIT_DISPATCH:
        # NOTE: Setting agent_name disables automatic dispatch. The agent must be explicitly dispatched
        # (e.g., via SIP dispatch rule `room_config.agents`).
        server.rtc_session(agent_name=settings.LIVEKIT_PHONE_AGENT_NAME)(phone_agent_entrypoint)
        logger.info("phone_agent_dispatch_mode_configured", dispatch_mode="explicit")
        return

    # Default: automatic dispatch (agent joins each new room without needing explicit dispatch rules).
    server.rtc_session()(phone_agent_entrypoint)
    logger.info("phone_agent_dispatch_mode_configured", dispatch_mode="automatic")


async def phone_agent_entrypoint(ctx: JobContext) -> None:
    """Handle an inbound RTC session (SIP caller) by starting the voice agent session."""
    call_logger = logger.bind(room=ctx.room.name, agent_name=settings.LIVEKIT_PHONE_AGENT_NAME)
    call_logger.info("phone_agent_call_received")

    try:
        call_logger.info(
            "phone_agent_session_initializing",
            has_google_api_key=bool(settings.GOOGLE_API_KEY),
            has_google_application_credentials=bool(settings.GOOGLE_APPLICATION_CREDENTIALS),
        )
        if "vad" not in ctx.proc.userdata:
            call_logger.error("phone_agent_missing_vad_in_userdata")
            return

        usage_collector = metrics.UsageCollector()
        session = _build_session(vad=ctx.proc.userdata["vad"])
        _bind_metrics_handlers(session=session, usage_collector=usage_collector)

        async def _log_usage() -> None:
            summary = usage_collector.get_summary()
            call_logger.info("phone_agent_usage_summary", summary=summary)

        ctx.add_shutdown_callback(_log_usage)

        await session.start(
            agent=create_phone_agent(),
            room=ctx.room,
            room_options=_build_room_options(),
        )
        call_logger.info("phone_agent_session_started")

        # NOTE: In livekit-agents 1.3.x, generate_reply() is synchronous and returns a SpeechHandle.
        # Awaiting it will raise and the agent will never speak.
        session.generate_reply()
        call_logger.info("phone_agent_initial_reply_requested")
    except Exception:
        call_logger.exception("phone_agent_entrypoint_failed")
        raise


def build_server() -> AgentServer:
    """Build and configure the LiveKit `AgentServer` for the phone agent."""
    logger.info(
        "phone_agent_server_building",
        agent_name=settings.LIVEKIT_PHONE_AGENT_NAME,
        voice=settings.LIVEKIT_PHONE_AGENT_VOICE,
        explicit_dispatch=settings.LIVEKIT_PHONE_AGENT_EXPLICIT_DISPATCH,
    )

    if not settings.LIVEKIT_URL or not settings.LIVEKIT_API_KEY or not settings.LIVEKIT_API_SECRET:
        logger.warning(
            "phone_agent_missing_livekit_credentials",
            has_livekit_url=bool(settings.LIVEKIT_URL),
            has_livekit_api_key=bool(settings.LIVEKIT_API_KEY),
            has_livekit_api_secret=bool(settings.LIVEKIT_API_SECRET),
        )

    if not settings.GOOGLE_API_KEY and not settings.GOOGLE_APPLICATION_CREDENTIALS:
        logger.warning(
            "phone_agent_missing_google_credentials",
            has_google_api_key=bool(settings.GOOGLE_API_KEY),
            has_google_application_credentials=bool(settings.GOOGLE_APPLICATION_CREDENTIALS),
        )

    server = AgentServer()
    server.setup_fnc = _prewarm
    _register_entrypoint(server)

    return server


def run() -> None:
    """Run the LiveKit agent app (supports `dev`, `console`, etc.)."""
    logger.info("phone_agent_cli_starting")
    cli.run_app(build_server())


if __name__ == "__main__":
    run()
