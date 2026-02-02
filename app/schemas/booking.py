"""Booking domain schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.enums import ActorType, BookingEventType, BookingStatus, SourceChannel


class BookingBase(SQLModel):
    business_id: UUID
    branch_id: UUID
    service_id: UUID
    customer_id: UUID
    booking_number: str
    start_at: datetime
    end_at: datetime
    status: BookingStatus = BookingStatus.active
    source_channel: SourceChannel
    customer_note: Optional[str] = None
    internal_note: Optional[str] = None
    last_confirmed_version_id: Optional[UUID] = None
    created_by_type: ActorType
    cancelled_at: Optional[datetime] = None


class BookingCreate(BookingBase):
    pass


class BookingUpdate(SQLModel):
    business_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    service_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    booking_number: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    status: Optional[BookingStatus] = None
    source_channel: Optional[SourceChannel] = None
    customer_note: Optional[str] = None
    internal_note: Optional[str] = None
    last_confirmed_version_id: Optional[UUID] = None
    created_by_type: Optional[ActorType] = None
    cancelled_at: Optional[datetime] = None


class BookingRead(BookingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class BookingVersionBase(SQLModel):
    booking_id: UUID
    version_number: int
    snapshot: Dict[str, Any]
    created_by_type: ActorType
    created_by_id: Optional[UUID] = None


class BookingVersionCreate(BookingVersionBase):
    pass


class BookingVersionUpdate(SQLModel):
    booking_id: Optional[UUID] = None
    version_number: Optional[int] = None
    snapshot: Optional[Dict[str, Any]] = None
    created_by_type: Optional[ActorType] = None
    created_by_id: Optional[UUID] = None


class BookingVersionRead(BookingVersionBase):
    id: UUID
    created_at: datetime


class BookingEventBase(SQLModel):
    booking_id: UUID
    event_type: BookingEventType
    actor_type: ActorType
    actor_id: Optional[UUID] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class BookingEventCreate(BookingEventBase):
    pass


class BookingEventUpdate(SQLModel):
    booking_id: Optional[UUID] = None
    event_type: Optional[BookingEventType] = None
    actor_type: Optional[ActorType] = None
    actor_id: Optional[UUID] = None
    payload: Optional[Dict[str, Any]] = None


class BookingEventRead(BookingEventBase):
    id: UUID
    created_at: datetime
