"""Customer domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.common import utc_now
from app.models.enums import RecordStatus, UserIdentifierType


class CustomerProfile(SQLModel, table=True):
    """Customer profile data."""

    __tablename__ = "customer_profiles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    user_id: UUID
    display_name: Optional[str] = None
    telno: Optional[str] = None
    line_user_id: Optional[str] = None
    notes: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class CustomerUser(SQLModel, table=True):
    """Customer user account (UUID-based)."""

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    status: RecordStatus = Field(default=RecordStatus.active)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class UserIdentifier(SQLModel, table=True):
    """User identifiers."""

    __tablename__ = "user_identifiers"
    model_config = ConfigDict(populate_by_name=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    customer_id: UUID
    business_id: UUID
    type: UserIdentifierType
    identifier: str
    is_verified: bool = Field(default=False)
    verified_at: Optional[datetime] = None
    status: RecordStatus = Field(default=RecordStatus.active)
    metadata_: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column("metadata", JSONB),
        alias="metadata",
    )
    created_at: datetime = Field(default_factory=utc_now)
