"""Business domain models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from app.models.common import utc_now
from app.models.enums import BranchStatus, BusinessStatus, MembershipRole, MembershipStatus


class Business(SQLModel, table=True):
    """Business profile."""

    __tablename__ = "businesses"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    business_type: str
    timezone: str = Field(default="Asia/Bangkok")
    location: Optional[str] = None
    logo_url: Optional[str] = None
    status: BusinessStatus = Field(default=BusinessStatus.active)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Branch(SQLModel, table=True):
    """Business branches."""

    __tablename__ = "branches"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    name: str
    location: Optional[str] = None
    tel_no: Optional[str] = None
    status: BranchStatus = Field(default=BranchStatus.open)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Service(SQLModel, table=True):
    """Services provided by a branch."""

    __tablename__ = "services"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    branch_id: UUID
    business_id: UUID
    name: str
    duration_minutes: int
    price_amount: Optional[Decimal] = None
    price_currency: Optional[str] = None
    deposit_required: bool = Field(default=False)
    deposit_amount: Optional[Decimal] = None
    active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class BusinessMembership(SQLModel, table=True):
    """Admin membership within a business."""

    __tablename__ = "business_memberships"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    admin_user_id: UUID
    role: MembershipRole
    status: MembershipStatus = Field(default=MembershipStatus.active)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
