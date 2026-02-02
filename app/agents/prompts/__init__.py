"""This file contains the prompts for the agent."""

from datetime import datetime

from app.agents.config import settings
from app.agents.prompts.phone_agent import PHONE_AGENT_PROMPT_TEMPLATE
from app.agents.prompts.system import SYSTEM_PROMPT_TEMPLATE


def _format_prompt(template: str, **kwargs) -> str:
    """Format a prompt template with common variables."""
    return template.format(
        agent_name=settings.PROJECT_NAME + " Agent",
        current_date_and_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **kwargs,
    )


def load_system_prompt(**kwargs):
    """Load the system prompt."""
    return _format_prompt(SYSTEM_PROMPT_TEMPLATE, **kwargs)


def load_phone_agent_prompt(**kwargs):
    """Load the phone agent prompt."""
    return _format_prompt(PHONE_AGENT_PROMPT_TEMPLATE, **kwargs)
