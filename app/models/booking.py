"""Booking domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.common import utc_now
from app.models.enums import ActorType, BookingEventType, BookingStatus, SourceChannel


class Booking(SQLModel, table=True):
    """Booking data."""

    __tablename__ = "bookings"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    branch_id: UUID
    service_id: UUID
    customer_id: UUID
    booking_number: str
    start_at: datetime
    end_at: datetime
    status: BookingStatus = Field(default=BookingStatus.active)
    source_channel: SourceChannel
    customer_note: Optional[str] = None
    internal_note: Optional[str] = None
    last_confirmed_version_id: Optional[UUID] = None
    created_by_type: ActorType
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    cancelled_at: Optional[datetime] = None


class BookingVersion(SQLModel, table=True):
    """Snapshot versions of a booking."""

    __tablename__ = "booking_versions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID
    version_number: int
    snapshot: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    created_by_type: ActorType
    created_by_id: Optional[UUID] = None
    created_at: datetime = Field(default_factory=utc_now)


class BookingEvent(SQLModel, table=True):
    """Booking event audit log."""

    __tablename__ = "booking_events"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    booking_id: UUID
    event_type: BookingEventType
    actor_type: ActorType
    actor_id: Optional[UUID] = None
    payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=utc_now)
