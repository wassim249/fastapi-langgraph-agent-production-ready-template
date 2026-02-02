"""Business domain schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlmodel import SQLModel

from app.models.enums import BranchStatus, BusinessStatus, MembershipRole, MembershipStatus


class BusinessBase(SQLModel):
    name: str
    business_type: str
    timezone: str = "Asia/Bangkok"
    location: Optional[str] = None
    logo_url: Optional[str] = None
    status: BusinessStatus = BusinessStatus.active


class BusinessCreate(BusinessBase):
    pass


class BusinessUpdate(SQLModel):
    name: Optional[str] = None
    business_type: Optional[str] = None
    timezone: Optional[str] = None
    location: Optional[str] = None
    logo_url: Optional[str] = None
    status: Optional[BusinessStatus] = None


class BusinessRead(BusinessBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class BranchBase(SQLModel):
    business_id: UUID
    name: str
    location: Optional[str] = None
    tel_no: Optional[str] = None
    status: BranchStatus = BranchStatus.open


class BranchCreate(BranchBase):
    pass


class BranchUpdate(SQLModel):
    business_id: Optional[UUID] = None
    name: Optional[str] = None
    location: Optional[str] = None
    tel_no: Optional[str] = None
    status: Optional[BranchStatus] = None


class BranchRead(BranchBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class ServiceBase(SQLModel):
    branch_id: UUID
    business_id: UUID
    name: str
    duration_minutes: int
    price_amount: Optional[Decimal] = None
    price_currency: Optional[str] = None
    deposit_required: bool = False
    deposit_amount: Optional[Decimal] = None
    active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(SQLModel):
    branch_id: Optional[UUID] = None
    business_id: Optional[UUID] = None
    name: Optional[str] = None
    duration_minutes: Optional[int] = None
    price_amount: Optional[Decimal] = None
    price_currency: Optional[str] = None
    deposit_required: Optional[bool] = None
    deposit_amount: Optional[Decimal] = None
    active: Optional[bool] = None


class ServiceRead(ServiceBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class BusinessMembershipBase(SQLModel):
    business_id: UUID
    admin_user_id: UUID
    role: MembershipRole
    status: MembershipStatus = MembershipStatus.active


class BusinessMembershipCreate(BusinessMembershipBase):
    pass


class BusinessMembershipUpdate(SQLModel):
    business_id: Optional[UUID] = None
    admin_user_id: Optional[UUID] = None
    role: Optional[MembershipRole] = None
    status: Optional[MembershipStatus] = None


class BusinessMembershipRead(BusinessMembershipBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
