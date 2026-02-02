"""Notification domain schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.enums import NotificationChannel, NotificationJobStatus, NotificationTemplate


class NotificationJobBase(SQLModel):
    business_id: UUID
    booking_id: Optional[UUID] = None
    channel: NotificationChannel
    template: NotificationTemplate
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    status: NotificationJobStatus = NotificationJobStatus.queued
    provider_reference: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)


class NotificationJobCreate(NotificationJobBase):
    pass


class NotificationJobUpdate(SQLModel):
    business_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None
    channel: Optional[NotificationChannel] = None
    template: Optional[NotificationTemplate] = None
    scheduled_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    status: Optional[NotificationJobStatus] = None
    provider_reference: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class NotificationJobRead(NotificationJobBase):
    id: UUID
    created_at: datetime
