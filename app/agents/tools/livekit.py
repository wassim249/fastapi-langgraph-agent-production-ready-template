"""Core LiveKit tools (call/session control).

These tools are intentionally business-agnostic and focus on core call control behaviors.
"""

from livekit.agents import (
    RunContext,
    function_tool,
)

from app.agents.logging import logger


@function_tool
async def end_call(context: RunContext) -> str:
    """End the call gracefully.

    Note: In many telephony setups, the agent saying goodbye and becoming silent is sufficient.
    If you later want hard hangup behavior, wire that via SIP provider settings or session APIs.
    """
    _ = context
    logger.info("phone_agent_end_call_requested")
    return "Thank you for calling. Have a great day. Goodbye."


LIVEKIT_CORE_TOOLS = [
    end_call,
]
