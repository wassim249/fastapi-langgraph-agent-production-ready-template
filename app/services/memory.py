"""Long-term memory service using mem0 and pgvector with optional cache layer."""

from langchain_core.messages import BaseMessage
from mem0 import AsyncMemory

from app.core.cache import (
    cache_key,
    cache_service,
)
from app.core.config import settings
from app.core.logging import logger
from app.core.prompts import load_memory_capture_prompt
from app.utils import latest_turn_text


class MemoryService:
    """Service for managing long-term memory using mem0 and pgvector."""

    def __init__(self):
        """Initialize the memory service."""
        self._memory: AsyncMemory = None

    async def _get_memory(self) -> AsyncMemory:
        if self._memory is None:
            self._memory = await AsyncMemory.from_config(
                config_dict={
                    "vector_store": {
                        "provider": "pgvector",
                        "config": {
                            "collection_name": settings.LONG_TERM_MEMORY_COLLECTION_NAME,
                            "dbname": settings.POSTGRES_DB,
                            "user": settings.POSTGRES_USER,
                            "password": settings.POSTGRES_PASSWORD,
                            "host": settings.POSTGRES_HOST,
                            "port": settings.POSTGRES_PORT,
                        },
                    },
                    "llm": {
                        "provider": "openai",
                        "config": {"model": settings.LONG_TERM_MEMORY_MODEL},
                    },
                    "embedder": {
                        "provider": "openai",
                        "config": {"model": settings.LONG_TERM_MEMORY_EMBEDDER_MODEL},
                    },
                    "custom_fact_extraction_prompt": load_memory_capture_prompt(),
                }
            )
        return self._memory

    async def initialize(self) -> None:
        """Pre-warm the mem0 AsyncMemory instance and its pgvector connection pool.

        Call once at startup so the first search() or add() doesn't pay the
        ~130ms from_config + pgvector.list_cols() cold-init cost.
        """
        await self._get_memory()
        logger.info("memory_service_initialized")

    async def search(self, user_id: str, query: str) -> str:
        """Search relevant memories for a user.

        Checks cache first; on miss, queries mem0 and caches the result.

        Returns formatted memory string, or empty string on failure.
        """
        try:
            # Check cache first
            key = cache_key("memory", str(user_id), query)
            cached = await cache_service.get(key)
            if cached is not None:
                logger.debug("memory_search_cache_hit", user_id=user_id)
                return cached

            memory = await self._get_memory()
            results = await memory.search(user_id=str(user_id), query=query)
            result = "\n".join([f"* {r['memory']}" for r in results["results"]])

            # Cache successful results
            if result:
                await cache_service.set(key, result)

            return result
        except Exception as e:
            logger.error("failed_to_get_relevant_memory", error=str(e), user_id=user_id, query=query)
            return ""

    async def add(self, user_id: str, messages: list[BaseMessage]) -> None:
        """Add the latest user turn to long-term memory.

        Only the latest user message is forwarded to mem0. The assistant reply
        is deliberately excluded: mem0's extractor concatenates both roles and
        paraphrases the assistant's suggestions as if the user had volunteered
        them, producing noisy facts.
        """
        user_text, _ = latest_turn_text(messages)
        user_text = (user_text or "").strip()
        if not user_text:
            logger.debug("long_term_memory_skipped_empty_turn", user_id=user_id)
            return

        try:
            memory = await self._get_memory()
            await memory.add(
                [{"role": "user", "content": user_text}],
                user_id=str(user_id),
            )
            logger.info("long_term_memory_updated_successfully", user_id=user_id)
        except Exception as e:
            logger.exception("failed_to_update_long_term_memory", user_id=user_id, error=str(e))


memory_service = MemoryService()
