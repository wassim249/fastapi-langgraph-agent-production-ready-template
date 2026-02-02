"""Admin domain schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from app.models.enums import AdminIdentifierType, RecordStatus


class AdminProfileBase(SQLModel):
    email: str
    telno: Optional[str] = None
    name: str
    status: RecordStatus = RecordStatus.active


class AdminProfileCreate(AdminProfileBase):
    pass


class AdminProfileUpdate(SQLModel):
    email: Optional[str] = None
    telno: Optional[str] = None
    name: Optional[str] = None
    status: Optional[RecordStatus] = None


class AdminProfileRead(AdminProfileBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class AdminIdentifierBase(SQLModel):
    model_config = ConfigDict(populate_by_name=True)

    admin_id: UUID
    type: AdminIdentifierType
    identifier: str
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    status: RecordStatus = RecordStatus.active
    metadata_: Dict[str, Any] = Field(default_factory=dict, alias="metadata")


class AdminIdentifierCreate(AdminIdentifierBase):
    pass


class AdminIdentifierUpdate(SQLModel):
    model_config = ConfigDict(populate_by_name=True)

    admin_id: Optional[UUID] = None
    type: Optional[AdminIdentifierType] = None
    identifier: Optional[str] = None
    is_verified: Optional[bool] = None
    verified_at: Optional[datetime] = None
    status: Optional[RecordStatus] = None
    metadata_: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")


class AdminIdentifierRead(AdminIdentifierBase):
    id: UUID
    created_at: datetime
