"""Payment domain models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from app.models.common import utc_now
from app.models.enums import PaymentIntentStatus, PaymentProvider, PaymentSettingStatus, PaymentTxStatus


class PaymentSetting(SQLModel, table=True):
    """Payment settings for a business."""

    __tablename__ = "payment_settings"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    provider: PaymentProvider
    status: PaymentSettingStatus = Field(default=PaymentSettingStatus.active)
    config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PaymentIntent(SQLModel, table=True):
    """Payment intent data."""

    __tablename__ = "payment_intents"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    business_id: UUID
    booking_id: UUID
    provider: PaymentProvider
    amount: Decimal
    currency: str
    status: PaymentIntentStatus = Field(default=PaymentIntentStatus.created)
    expires_at: Optional[datetime] = None
    provider_reference: Optional[str] = None
    qr_payload: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class PaymentTransaction(SQLModel, table=True):
    """Payment transaction records."""

    __tablename__ = "payment_transactions"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    payment_intent_id: UUID
    status: PaymentTxStatus
    provider_payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSONB))
    processed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=utc_now)
