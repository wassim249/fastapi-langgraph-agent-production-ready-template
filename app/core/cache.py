"""Cache service with optional Redis/Valkey backend.

If VALKEY_HOST is configured, uses Redis client to connect to Valkey for distributed caching.
Otherwise, falls back to a simple in-memory TTL cache.
"""

import hashlib
import time
from typing import (
    TYPE_CHECKING,
    Awaitable,
    Optional,
    cast,
)

from app.core.config import settings
from app.core.logging import logger

# Try to import redis — it's an optional dependency
if TYPE_CHECKING:
    from redis.asyncio import Redis  # pyright: ignore[reportMissingImports]

    REDIS_AVAILABLE = True
else:
    try:
        from redis.asyncio import Redis

        REDIS_AVAILABLE = True
    except ImportError:
        logger.debug("redis_not_available")
        Redis = None
        REDIS_AVAILABLE = False


class InMemoryCacheService:
    """Simple in-memory TTL cache fallback when Valkey is not available."""

    def __init__(self, default_ttl: int = 60):
        """Initialize in-memory cache.

        Args:
            default_ttl: Default time-to-live in seconds for cache entries.
        """
        self._cache: dict[str, tuple[float, str]] = {}
        self._default_ttl = default_ttl

    async def initialize(self) -> None:
        """No-op for in-memory cache."""
        logger.info("cache_initialized", backend="in_memory", ttl=self._default_ttl)

    async def get(self, key: str) -> Optional[str]:
        """Get a value from cache.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if not found or expired.
        """
        entry = self._cache.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._cache[key]
            return None
        return value

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value in cache with TTL.

        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Time-to-live in seconds. Uses default if not specified.
        """
        expires_at = time.monotonic() + (ttl or self._default_ttl)
        self._cache[key] = (expires_at, value)

    async def delete(self, key: str) -> None:
        """Delete a value from cache.

        Args:
            key: The cache key.
        """
        self._cache.pop(key, None)

    async def close(self) -> None:
        """Clear the in-memory cache."""
        self._cache.clear()


class ValkeyCacheService:
    """Redis/Valkey cache backend for distributed caching."""

    def __init__(self, default_ttl: int = 60):
        """Initialize cache service with Redis client.

        Args:
            default_ttl: Default time-to-live in seconds for cache entries.
        """
        self._client: Optional[Redis] = None
        self._default_ttl = default_ttl

    async def initialize(self) -> None:
        """Connect to Redis/Valkey server."""
        client = Redis(
            host=settings.VALKEY_HOST,
            port=settings.VALKEY_PORT,
            db=settings.VALKEY_DB,
            password=settings.VALKEY_PASSWORD or None,
            max_connections=settings.VALKEY_MAX_CONNECTIONS,
            decode_responses=True,
        )
        await cast(Awaitable[bool], client.ping())
        self._client = client
        logger.info(
            "cache_initialized",
            backend="redis",
            host=settings.VALKEY_HOST,
            port=settings.VALKEY_PORT,
            ttl=self._default_ttl,
        )

    async def get(self, key: str) -> Optional[str]:
        """Get a value from Valkey.

        Args:
            key: The cache key.

        Returns:
            The cached value, or None if not found.
        """
        if not self._client:
            return None
        try:
            return await self._client.get(key)
        except Exception as e:
            logger.warning("cache_get_failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        """Set a value in Valkey with TTL.

        Args:
            key: The cache key.
            value: The value to cache.
            ttl: Time-to-live in seconds. Uses default if not specified.
        """
        if not self._client:
            return
        try:
            await self._client.set(key, value, ex=(ttl or self._default_ttl))
        except Exception as e:
            logger.warning("cache_set_failed", key=key, error=str(e))

    async def delete(self, key: str) -> None:
        """Delete a value from Valkey.

        Args:
            key: The cache key.
        """
        if not self._client:
            return
        try:
            await self._client.delete(key)
        except Exception as e:
            logger.warning("cache_delete_failed", key=key, error=str(e))

    async def close(self) -> None:
        """Close the Valkey connection."""
        if self._client:
            await self._client.aclose()
            logger.info("cache_connection_closed")


def _create_cache_service() -> InMemoryCacheService | ValkeyCacheService:
    """Create the appropriate cache service based on configuration.

    Returns:
        A cache service instance (Redis if configured, otherwise in-memory).
    """
    ttl = settings.CACHE_TTL_SECONDS

    if settings.VALKEY_HOST and REDIS_AVAILABLE:
        return ValkeyCacheService(default_ttl=ttl)

    if settings.VALKEY_HOST and not REDIS_AVAILABLE:
        logger.warning(
            "redis_client_not_installed",
            hint="install with: uv add redis --optional cache",
        )

    return InMemoryCacheService(default_ttl=ttl)


def cache_key(prefix: str, *parts: str) -> str:
    """Build a cache key with a prefix and hashed parts.

    Args:
        prefix: The cache key prefix (e.g., "memory").
        *parts: Additional parts to include in the key.

    Returns:
        A deterministic cache key string.
    """
    raw = ":".join(parts)
    hashed = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"{prefix}:{hashed}"


# Global cache service singleton — initialized lazily in lifespan
cache_service = _create_cache_service()
