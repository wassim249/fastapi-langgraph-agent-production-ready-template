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
    """Called when the user wants to end the call or says goodbye.

    Returns:
        Farewell message
    """
    logger.info("User requested to end call")
    return "Thank you for calling! Have a great day. Goodbye!"
