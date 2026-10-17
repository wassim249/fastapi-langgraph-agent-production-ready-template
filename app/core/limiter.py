"""Rate limiting configuration for the application.

This module configures rate limiting using slowapi, with default limits
defined in the application settings. Rate limits are applied based on
remote IP addresses.

When Valkey is configured, uses it as a distributed storage backend
so rate limits work correctly across multiple app instances.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.cache import REDIS_AVAILABLE
from app.core.config import settings
from app.core.logging import logger

# Build storage URI for Valkey if configured. redis is an optional dependency
# (the `cache` extra), so fall back to in-memory storage when it is missing
# rather than letting limits raise ConfigurationError at import time.
_storage_uri = None
if settings.VALKEY_HOST and REDIS_AVAILABLE:
    _password_part = f":{settings.VALKEY_PASSWORD}@" if settings.VALKEY_PASSWORD else ""
    _storage_uri = f"redis://{_password_part}{settings.VALKEY_HOST}:{settings.VALKEY_PORT}/{settings.VALKEY_DB}"
    logger.info("rate_limiter_using_valkey", host=settings.VALKEY_HOST, port=settings.VALKEY_PORT)
elif settings.VALKEY_HOST:
    logger.warning(
        "rate_limiter_valkey_configured_but_redis_missing",
        hint="install with: uv add redis --optional cache",
    )

# Initialize rate limiter (uses in-memory storage if no Valkey)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=settings.RATE_LIMIT_DEFAULT,  # pyright: ignore[reportArgumentType]
    storage_uri=_storage_uri,
)
