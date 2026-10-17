"""Observability module for the application."""

from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from app.core.config import settings
from app.core.logging import logger


def langfuse_init():
    """Initialize Langfuse."""
    if not settings.LANGFUSE_TRACING_ENABLED:
        logger.debug("langfuse_tracing_disabled")
        return

    langfuse = Langfuse(
        tracing_enabled=settings.LANGFUSE_TRACING_ENABLED,
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        secret_key=settings.LANGFUSE_SECRET_KEY,
        host=settings.LANGFUSE_HOST,
        environment=settings.ENVIRONMENT.value,
        debug=settings.DEBUG,
    )

    try:
        if langfuse.auth_check():
            logger.debug("langfuse_auth_success")
        else:
            logger.warning("langfuse_auth_failure")
    except Exception:
        logger.exception("langfuse_auth_check_failed")


def get_langfuse_callback_handler() -> CallbackHandler:
    """Create a Langfuse CallbackHandler for tracking LLM interactions.

    Returns:
        CallbackHandler: Configured Langfuse callback handler.
    """
    return CallbackHandler()


langfuse_callback_handler = get_langfuse_callback_handler()
