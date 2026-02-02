"""Payment domain schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.enums import PaymentIntentStatus, PaymentProvider, PaymentSettingStatus, PaymentTxStatus


class PaymentSettingBase(SQLModel):
    business_id: UUID
    provider: PaymentProvider
    status: PaymentSettingStatus = PaymentSettingStatus.active
    config: Dict[str, Any] = Field(default_factory=dict)


class PaymentSettingCreate(PaymentSettingBase):
    pass


class PaymentSettingUpdate(SQLModel):
    business_id: Optional[UUID] = None
    provider: Optional[PaymentProvider] = None
    status: Optional[PaymentSettingStatus] = None
    config: Optional[Dict[str, Any]] = None


class PaymentSettingRead(PaymentSettingBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class PaymentIntentBase(SQLModel):
    business_id: UUID
    booking_id: UUID
    provider: PaymentProvider
    amount: Decimal
    currency: str
    status: PaymentIntentStatus = PaymentIntentStatus.created
    expires_at: Optional[datetime] = None
    provider_reference: Optional[str] = None
    qr_payload: Optional[Dict[str, Any]] = None


class PaymentIntentCreate(PaymentIntentBase):
    pass


class PaymentIntentUpdate(SQLModel):
    business_id: Optional[UUID] = None
    booking_id: Optional[UUID] = None
    provider: Optional[PaymentProvider] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    status: Optional[PaymentIntentStatus] = None
    expires_at: Optional[datetime] = None
    provider_reference: Optional[str] = None
    qr_payload: Optional[Dict[str, Any]] = None


class PaymentIntentRead(PaymentIntentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime


class PaymentTransactionBase(SQLModel):
    payment_intent_id: UUID
    status: PaymentTxStatus
    provider_payload: Dict[str, Any] = Field(default_factory=dict)
    processed_at: Optional[datetime] = None


class PaymentTransactionCreate(PaymentTransactionBase):
    pass


class PaymentTransactionUpdate(SQLModel):
    payment_intent_id: Optional[UUID] = None
    status: Optional[PaymentTxStatus] = None
    provider_payload: Optional[Dict[str, Any]] = None
    processed_at: Optional[datetime] = None


class PaymentTransactionRead(PaymentTransactionBase):
    id: UUID
    created_at: datetime
