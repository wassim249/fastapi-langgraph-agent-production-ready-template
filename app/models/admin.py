"""Admin domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import ConfigDict
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.common import utc_now
from app.models.enums import AdminIdentifierType, RecordStatus


class AdminProfile(SQLModel, table=True):
    """Admin profile data."""

    __tablename__ = "admin_profiles"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str
    telno: Optional[str] = None
    name: str
    status: RecordStatus = Field(default=RecordStatus.active)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class AdminIdentifier(SQLModel, table=True):
    """Admin identifiers."""

    __tablename__ = "admin_identifiers"
    model_config = ConfigDict(populate_by_name=True)

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    admin_id: UUID
    type: AdminIdentifierType
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
