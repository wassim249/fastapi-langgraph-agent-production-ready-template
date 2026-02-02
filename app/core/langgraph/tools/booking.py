"""Business-domain tools for appointment/booking flows (LiveKit function tools).

These tools represent your appointment/booking capabilities. They are designed for
voice usage (short inputs/outputs), and can be upgraded later to call internal services/DB.
"""

from livekit.agents import (
    RunContext,
    function_tool,
)

from app.core.logging import logger


@function_tool
async def get_business_hours(context: RunContext) -> str:
    """Return business hours information."""
    _ = context
    logger.info("phone_agent_business_hours_requested")
    return (
        "Our business hours are Monday through Friday, 9 AM to 5 PM Pacific Time. "
        "We are closed on weekends and major holidays."
    )


@function_tool
async def get_contact_info(context: RunContext) -> str:
    """Return contact information."""
    _ = context
    logger.info("phone_agent_contact_info_requested")
    return "You can reach us by email at support@example.com, or visit our website at www.example.com."


@function_tool
async def schedule_callback(
    context: RunContext,
    name: str,
    phone_number: str,
    preferred_time: str,
    reason: str,
) -> str:
    """Schedule a callback from a human representative."""
    _ = context
    logger.info(
        "phone_agent_callback_requested",
        name=name,
        phone_number=phone_number,
        preferred_time=preferred_time,
        reason=reason,
    )
    return (
        "I've scheduled a callback for you. "
        "A representative will call you at your preferred time. "
        "Is there anything else I can help you with?"
    )


@function_tool
async def check_availability(
    context: RunContext,
    branch: str,
    service: str,
    preferred_date: str,
    preferred_time: str,
) -> str:
    """Check appointment availability (placeholder).

    This is a stub for now. Replace with a real availability lookup (DB or internal API).
    """
    _ = context
    logger.info(
        "phone_agent_check_availability_requested",
        branch=branch,
        service=service,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
    )
    return (
        "I can help with that. Right now, I don't have live availability access. "
        "If you share a 1-2 hour window, I can propose a few options or schedule a callback for confirmation."
    )


@function_tool
async def create_booking(
    context: RunContext,
    customer_name: str,
    customer_phone: str,
    branch: str,
    service: str,
    date: str,
    time: str,
    notes: str = "",
) -> str:
    """Create a booking (placeholder).

    This is a stub for now. Replace with a real booking create (DB or internal API).
    """
    _ = context
    logger.info(
        "phone_agent_create_booking_requested",
        customer_name=customer_name,
        customer_phone=customer_phone,
        branch=branch,
        service=service,
        date=date,
        time=time,
        has_notes=bool(notes),
    )
    return (
        "Thanks. I have the details as:\n"
        f"- Name: {customer_name}\n"
        f"- Phone: {customer_phone}\n"
        f"- Service: {service}\n"
        f"- Branch: {branch}\n"
        f"- Date/Time: {date} {time}\n"
        "Please confirm if everything is correct, and I will finalize the booking."
    )


BOOKING_TOOLS = [
    get_business_hours,
    get_contact_info,
    schedule_callback,
    check_availability,
    create_booking,
]
