"""Availability domain models."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import Field, SQLModel

from app.models.common import utc_now
from app.models.enums import AvailabilityRuleEffect, AvailabilitySlotStatus


class WeeklyAvailabilityRule(SQLModel, table=True):
    """Weekly recurring availability rules."""

    __tablename__ = "weekly_availability_rules"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    branch_id: UUID
    name: str
    days_of_week: List[int] = Field(sa_column=Column(ARRAY(Integer)))
    start_time_local: time
    end_time_local: time
    slot_interval_minutes: int
    active: bool = Field(default=True)
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class DatetimeAvailabilityRule(SQLModel, table=True):
    """Datetime-specific availability rules."""

    __tablename__ = "datetime_availability_rules"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    branch_id: UUID
    name: str
    rule_effect: AvailabilityRuleEffect = Field(default=AvailabilityRuleEffect.block)
    start_at: datetime
    end_at: datetime
    priority: int = Field(default=100)
    reason: Optional[str] = None
    active: bool = Field(default=True)
    created_by_admin_user_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class AvailabilitySlot(SQLModel, table=True):
    """Discrete availability slots."""

    __tablename__ = "availability_slots"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    branch_id: UUID
    start_at: datetime
    end_at: datetime
    capacity: int = Field(default=1)
    status: AvailabilitySlotStatus = Field(default=AvailabilitySlotStatus.open)
    held_by_booking_id: Optional[UUID] = None
    hold_expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)
