"""Notification domain models."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.common import utc_now
from app.models.enums import NotificationChannel, NotificationJobStatus, NotificationTemplate


class NotificationJob(SQLModel, table=True):
    """Notification delivery jobs."""

    __tablename__ = "notification_jobs"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    booking_id: Optional[UUID] = None
    channel: NotificationChannel
    template: NotificationTemplate
    scheduled_at: datetime
    sent_at: Optional[datetime] = None
    status: NotificationJobStatus = Field(default=NotificationJobStatus.queued)
    provider_reference: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=utc_now)
