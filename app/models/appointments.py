"""Backward-compatible aggregate exports for appointment domain models."""

from app.models.admin import AdminIdentifier, AdminProfile
from app.models.availability import AvailabilitySlot, DatetimeAvailabilityRule, WeeklyAvailabilityRule
from app.models.booking import Booking, BookingEvent, BookingVersion
from app.models.business import Branch, Business, BusinessMembership, Service
from app.models.common import utc_now
from app.models.customer import CustomerProfile, CustomerUser, UserIdentifier
from app.models.enums import (
    ActorType,
    AdminIdentifierType,
    AvailabilityRuleEffect,
    AvailabilitySlotStatus,
    BookingEventType,
    BookingStatus,
    BranchStatus,
    BusinessStatus,
    MembershipRole,
    MembershipStatus,
    NotificationChannel,
    NotificationJobStatus,
    NotificationTemplate,
    PaymentIntentStatus,
    PaymentProvider,
    PaymentSettingStatus,
    PaymentTxStatus,
    RecordStatus,
    SourceChannel,
    UserIdentifierType,
)
from app.models.notification import NotificationJob
from app.models.payment import PaymentIntent, PaymentSetting, PaymentTransaction

__all__ = [
    "AdminIdentifier",
    "AdminProfile",
    "AvailabilitySlot",
    "DatetimeAvailabilityRule",
    "WeeklyAvailabilityRule",
    "Booking",
    "BookingEvent",
    "BookingVersion",
    "Branch",
    "Business",
    "BusinessMembership",
    "Service",
    "CustomerProfile",
    "CustomerUser",
    "UserIdentifier",
    "NotificationJob",
    "PaymentIntent",
    "PaymentSetting",
    "PaymentTransaction",
    "utc_now",
    "ActorType",
    "AdminIdentifierType",
    "AvailabilityRuleEffect",
    "AvailabilitySlotStatus",
    "BookingEventType",
    "BookingStatus",
    "BranchStatus",
    "BusinessStatus",
    "MembershipRole",
    "MembershipStatus",
    "NotificationChannel",
    "NotificationJobStatus",
    "NotificationTemplate",
    "PaymentIntentStatus",
    "PaymentProvider",
    "PaymentSettingStatus",
    "PaymentTxStatus",
    "RecordStatus",
    "SourceChannel",
    "UserIdentifierType",
]
