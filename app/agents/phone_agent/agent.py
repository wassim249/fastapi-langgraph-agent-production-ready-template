"""Phone agent for LiveKit."""

from livekit.agents import Agent

from app.agents.prompts.phone_agent import PHONE_AGENT_PROMPT
from app.agents.tools.booking import get_business_hours, get_contact_info, schedule_callback
from app.agents.tools.livekit import end_call


def create_phone_agent() -> Agent:
    """Create and return the phone agent with all configured tools."""
    return Agent(
        instructions=PHONE_AGENT_PROMPT,
        tools=[
            get_business_hours,
            get_contact_info,
            schedule_callback,
            end_call,
        ],
    )
