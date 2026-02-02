"""Customer domain schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import ConfigDict
from sqlmodel import Field, SQLModel

from app.models.enums import RecordStatus, UserIdentifierType


class CustomerProfileBase(SQLModel):
    business_id: UUID
    user_id: UUID
    display_name: Optional[str] = None
    telno: Optional[str] = None
    line_user_id: Optional[str] = None
    notes: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None


class CustomerProfileCreate(CustomerProfileBase):
    pass


class CustomerProfileUpdate(SQLModel):
    business_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    display_name: Optional[str] = None
    telno: Optional[str] = None
    line_user_id: Optional[str] = None
    notes: Optional[str] = None
    locale: Optional[str] = None
    timezone: Optional[str] = None


class CustomerProfileRead(CustomerProfileBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class CustomerUserBase(SQLModel):
    status: RecordStatus = RecordStatus.active


class CustomerUserCreate(CustomerUserBase):
    pass


class CustomerUserUpdate(SQLModel):
    status: Optional[RecordStatus] = None


class CustomerUserRead(CustomerUserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class UserIdentifierBase(SQLModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: UUID
    type: UserIdentifierType
    identifier: str
    is_verified: bool = False
    verified_at: Optional[datetime] = None
    status: RecordStatus = RecordStatus.active
    metadata_: Dict[str, Any] = Field(default_factory=dict, alias="metadata")


class UserIdentifierCreate(UserIdentifierBase):
    pass


class UserIdentifierUpdate(SQLModel):
    model_config = ConfigDict(populate_by_name=True)

    customer_id: Optional[UUID] = None
    type: Optional[UserIdentifierType] = None
    identifier: Optional[str] = None
    is_verified: Optional[bool] = None
    verified_at: Optional[datetime] = None
    status: Optional[RecordStatus] = None
    metadata_: Optional[Dict[str, Any]] = Field(default=None, alias="metadata")


class UserIdentifierRead(UserIdentifierBase):
    id: UUID
    created_at: datetime
