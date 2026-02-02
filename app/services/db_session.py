"""Async database session utilities."""

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.logging import logger

DATABASE_URL = (
    f"postgresql+psycopg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}"
    f"@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
)

async_engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.POSTGRES_POOL_SIZE,
    max_overflow=settings.POSTGRES_MAX_OVERFLOW,
)

async_session_factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

logger.info("async_database_initialized", database=settings.POSTGRES_DB)


async def get_async_session() -> AsyncSession:
    """Yield an async database session."""
    async with async_session_factory() as session:
        yield session
