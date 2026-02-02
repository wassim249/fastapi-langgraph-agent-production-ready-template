"""Shared enums for appointment domain models."""

from enum import Enum


class RecordStatus(str, Enum):
    """Status for soft-deletable records."""

    active = "active"
    blocked = "blocked"
    deleted = "deleted"


class AdminIdentifierType(str, Enum):
    """Identifier types for admins."""

    line = "LINE"
    oauth = "OAUTH"


class BusinessStatus(str, Enum):
    """Business lifecycle status."""

    active = "active"
    inactive = "inactive"


class BranchStatus(str, Enum):
    """Branch operating status."""

    open = "open"
    closed = "closed"


class MembershipRole(str, Enum):
    """Business membership roles."""

    owner = "Owner"
    admin = "Admin"
    staff = "Staff"
    viewer = "Viewer"


class MembershipStatus(str, Enum):
    """Business membership status."""

    active = "active"
    inactive = "inactive"


class UserIdentifierType(str, Enum):
    """Identifier types for users."""

    line = "LINE"
    phone = "PHONE"
    oauth = "OAUTH"


class AvailabilityRuleEffect(str, Enum):
    """Availability rule effect."""

    block = "BLOCK"


class AvailabilitySlotStatus(str, Enum):
    """Availability slot status."""

    open = "Open"
    held = "Held"
    booked = "Booked"
    blocked = "Blocked"


class BookingStatus(str, Enum):
    """Booking lifecycle status."""

    active = "Active"
    pending_deposit = "PendingDeposit"
    customer_cancelled = "CustomerCancelled"
    admin_cancelled = "AdminCancelled"
    checked_in = "CheckedIn"
    completed = "Completed"
    no_show = "NoShow"
    expired = "Expired"


class SourceChannel(str, Enum):
    """Booking source channel."""

    line = "LINE"
    phone = "PHONE"
    admin = "ADMIN"


class ActorType(str, Enum):
    """Actor types for booking actions."""

    customer = "Customer"
    agent = "Agent"
    admin = "Admin"
    system = "System"


class BookingEventType(str, Enum):
    """Booking event types."""

    created = "Created"
    sent_to_customer = "SentToCustomer"
    customer_confirmed = "CustomerConfirmed"
    revised = "Revised"
    cancelled = "Cancelled"
    checked_in = "CheckedIn"
    completed = "Completed"
    no_show = "NoShow"
    deposit_requested = "DepositRequested"
    deposit_paid = "DepositPaid"
    expired = "Expired"


class PaymentProvider(str, Enum):
    """Payment providers."""

    promptpay = "PromptPay"
    truemoney = "TrueMoney"
    card = "Card"
    stripe = "Stripe"
    omise = "Omise"


class PaymentSettingStatus(str, Enum):
    """Payment setting status."""

    active = "active"
    inactive = "inactive"


class PaymentIntentStatus(str, Enum):
    """Payment intent status."""

    created = "Created"
    pending = "Pending"
    succeeded = "Succeeded"
    failed = "Failed"
    expired = "Expired"
    refunded = "Refunded"


class PaymentTxStatus(str, Enum):
    """Payment transaction status."""

    succeeded = "Succeeded"
    failed = "Failed"
    refunded = "Refunded"


class NotificationChannel(str, Enum):
    """Notification delivery channels."""

    line = "LINE"
    sms = "SMS"
    email = "EMAIL"


class NotificationTemplate(str, Enum):
    """Notification templates."""

    booking_created = "BookingCreated"
    needs_confirmation = "NeedsConfirmation"
    confirmed = "Confirmed"
    reminder_24h = "Reminder24h"
    reminder_2h = "Reminder2h"
    cancelled = "Cancelled"
    deposit_request = "DepositRequest"
    deposit_received = "DepositReceived"


class NotificationJobStatus(str, Enum):
    """Notification job status."""

    queued = "Queued"
    sent = "Sent"
    failed = "Failed"
    cancelled = "Cancelled"
