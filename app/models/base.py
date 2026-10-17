"""Base models and common imports for all models."""

from datetime import datetime, UTC
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    """Base model with common fields."""

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
