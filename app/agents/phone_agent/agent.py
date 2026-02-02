"""LiveKit Agent definition for the phone agent (Gemini Live runtime)."""

from livekit.agents import (
    Agent,
    RunContext,
    function_tool,
)

from app.agents.logging import logger

AGENT_INSTRUCTIONS = """You are Lumi, a friendly booking assistant for a Lumos Beauty Salon.
You are responsible for helping the user to book appointments with the salon.
You are also responsible for answering questions about the salon and its services.
You can speak multiple languages depending on the user's preference, but default to speaking Thai.
Your task is:
1. Greet the caller warmly and introduce yourself.
2. Ask for the caller's name.
3. Ask for the service they are interested in.
4. Ask for the branch they would like to book the service at.
5. Ask for the date and time they would like to book the service.
6. When confirmed, finalize the booking.
7. Thank the user for calling and ask if there is anything else you can help with."""


@function_tool
async def get_business_hours(context: RunContext) -> str:
    """Return business hours information."""
    logger.info("phone_agent_get_business_hours_called")
    return (
        "Our business hours are Monday through Friday, 9 AM to 5 PM Pacific Time. "
        "We are closed on weekends and major holidays."
    )


@function_tool
async def get_contact_info(context: RunContext) -> str:
    """Return contact information."""
    logger.info("phone_agent_get_contact_info_called")
    return (
        "You can reach us by email at support@example.com, "
        "or visit our website at www.example.com for more information."
    )


@function_tool
async def schedule_callback(
    context: RunContext,
    name: str,
    phone_number: str,
    preferred_time: str,
    reason: str,
) -> str:
    """Schedule a callback (stub implementation)."""
    logger.info(
        "phone_agent_schedule_callback_requested",
        name=name,
        phone_number=phone_number,
        preferred_time=preferred_time,
        reason=reason,
    )
    return (
        f"I've scheduled a callback for {name} at {phone_number}. "
        f"A representative will call you {preferred_time}. "
        "Is there anything else I can help you with?"
    )


@function_tool
async def end_call(context: RunContext) -> str:
    """Return a farewell message."""
    logger.info("phone_agent_end_call_called")
    return "Thank you for calling! Have a great day. Goodbye!"


PHONE_AGENT_TOOLS = [
    get_business_hours,
    get_contact_info,
    schedule_callback,
    end_call,
]


def create_phone_agent() -> Agent:
    """Create and return the phone agent with all configured tools."""
    return Agent(
        instructions=AGENT_INSTRUCTIONS,
        tools=PHONE_AGENT_TOOLS,
    )
