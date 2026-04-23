"""This file contains the prompts for the agent."""

import os
from datetime import datetime
from typing import Optional

from app.core.config import settings

_PROMPTS_DIR = os.path.dirname(__file__)

# Read templates once at module load — no file I/O per request
with open(os.path.join(_PROMPTS_DIR, "system.md"), "r") as _f:
    _SYSTEM_PROMPT_TEMPLATE = _f.read()

with open(os.path.join(_PROMPTS_DIR, "session_title.md"), "r") as _f:
    SESSION_TITLE_PROMPT = _f.read()

with open(os.path.join(_PROMPTS_DIR, "memory_capture.md"), "r") as _f:
    _MEMORY_CAPTURE_PROMPT_TEMPLATE = _f.read()


def load_system_prompt(username: Optional[str] = None, **kwargs):
    """Load the system prompt from the cached template."""
    user_context = f"# User\nYou are talking to {username}.\n" if username else ""
    return _SYSTEM_PROMPT_TEMPLATE.format(
        agent_name=settings.PROJECT_NAME + " Agent",
        current_date_and_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        user_context=user_context,
        **kwargs,
    )


def load_memory_capture_prompt() -> str:
    """Render the memory-capture prompt with today's date.

    Uses ``str.replace`` rather than ``str.format`` because the prompt body
    contains literal JSON examples with curly braces that would break format().
    """
    return _MEMORY_CAPTURE_PROMPT_TEMPLATE.replace("{current_date}", datetime.now().strftime("%Y-%m-%d"))
