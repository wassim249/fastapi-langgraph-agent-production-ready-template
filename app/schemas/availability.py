"""Availability domain schemas."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID

from sqlmodel import SQLModel

from app.models.enums import AvailabilityRuleEffect, AvailabilitySlotStatus


class WeeklyAvailabilityRuleBase(SQLModel):
    business_id: UUID
    branch_id: UUID
    name: str
    days_of_week: List[int]
    start_time_local: time
    end_time_local: time
    slot_interval_minutes: int
    active: bool = True
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class WeeklyAvailabilityRuleCreate(WeeklyAvailabilityRuleBase):
    pass


class WeeklyAvailabilityRuleUpdate(SQLModel):
    business_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    name: Optional[str] = None
    days_of_week: Optional[List[int]] = None
    start_time_local: Optional[time] = None
    end_time_local: Optional[time] = None
    slot_interval_minutes: Optional[int] = None
    active: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None


class WeeklyAvailabilityRuleRead(WeeklyAvailabilityRuleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class DatetimeAvailabilityRuleBase(SQLModel):
    business_id: UUID
    branch_id: UUID
    name: str
    rule_effect: AvailabilityRuleEffect = AvailabilityRuleEffect.block
    start_at: datetime
    end_at: datetime
    priority: int = 100
    reason: Optional[str] = None
    active: bool = True
    created_by_admin_user_id: Optional[UUID] = None


class DatetimeAvailabilityRuleCreate(DatetimeAvailabilityRuleBase):
    pass


class DatetimeAvailabilityRuleUpdate(SQLModel):
    business_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    name: Optional[str] = None
    rule_effect: Optional[AvailabilityRuleEffect] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    priority: Optional[int] = None
    reason: Optional[str] = None
    active: Optional[bool] = None
    created_by_admin_user_id: Optional[UUID] = None


class DatetimeAvailabilityRuleRead(DatetimeAvailabilityRuleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class AvailabilitySlotBase(SQLModel):
    business_id: UUID
    branch_id: UUID
    start_at: datetime
    end_at: datetime
    capacity: int = 1
    status: AvailabilitySlotStatus = AvailabilitySlotStatus.open
    held_by_booking_id: Optional[UUID] = None
    hold_expires_at: Optional[datetime] = None


class AvailabilitySlotCreate(AvailabilitySlotBase):
    pass


class AvailabilitySlotUpdate(SQLModel):
    business_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    capacity: Optional[int] = None
    status: Optional[AvailabilitySlotStatus] = None
    held_by_booking_id: Optional[UUID] = None
    hold_expires_at: Optional[datetime] = None


class AvailabilitySlotRead(AvailabilitySlotBase):
    id: UUID
    created_at: datetime
