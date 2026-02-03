"""LiveKit Agents executor for inbound phone calls using Gemini Live (speech-to-speech)."""

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

from app.agents.logging import logger
from app.agents.phone_agent.agent import create_phone_agent

server = AgentServer(num_idle_processes=2)


def _prewarm(proc: JobProcess) -> None:
    """Prewarm function to load models before handling calls."""
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = _prewarm


@server.rtc_session()
async def entrypoint(ctx: JobContext):
    """
    Main entrypoint for handling incoming phone calls.

    This function is called when a new SIP participant (phone caller) joins.
    The dispatch rule configured in LiveKit routes each caller to their own room.
    """
    # Add context fields for logging
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    logger.info(f"New call received in room: {ctx.room.name}")

    session = AgentSession(
        vad=ctx.proc.userdata["vad"],
        llm=google.realtime.RealtimeModel(voice="Despina"),
    )

    # Set up metrics collection for monitoring
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        """Log usage summary when the call ends."""
        summary = usage_collector.get_summary()
        logger.info(f"Call ended. Usage summary: {summary}")

    # Register shutdown callback to log usage when call ends
    ctx.add_shutdown_callback(log_usage)

    @session.on("disconnected")
    def _on_disconnected():
        """Handle session disconnection."""
        logger.info("session_disconnected", room=ctx.room.name)

    @session.on("error")
    def _on_error(error: Exception):
        """Handle session errors."""
        logger.exception("session_error", room=ctx.room.name, error=str(error))

    # Start the session with our phone agent
    await session.start(
        agent=create_phone_agent(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            close_on_disconnect=True,
            delete_room_on_close=True,
            audio_input=room_io.AudioInputOptions(
                # Audio processing options for phone quality
            ),
        ),
    )

    # Generate an initial greeting for the caller
    session.generate_reply()


def run():
    """Run the phone agent."""
    cli.run_app(server)
