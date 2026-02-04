"""initial schema

Revision ID: 20260201_000001
Revises: 
Create Date: 2026-02-01 00:00:01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260201_000001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # Create function to validate days_of_week array (0-6 range)
    # This is needed because PostgreSQL doesn't allow subqueries in CHECK constraints
    op.execute("""
        CREATE OR REPLACE FUNCTION validate_days_of_week(days INTEGER[]) RETURNS BOOLEAN AS $$
        BEGIN
            IF array_length(days, 1) IS NULL THEN
                RETURN FALSE;
            END IF;
            RETURN (SELECT bool_and(d BETWEEN 0 AND 6) FROM unnest(days) AS d);
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
    """)

    # Create enum types using raw SQL with IF NOT EXISTS for idempotency
    # This prevents errors if the migration is run multiple times or partially
    enum_definitions = [
        ("record_status", "('active', 'blocked', 'deleted')"),
        ("membership_role", "('Owner', 'Admin', 'Staff', 'Viewer')"),
        ("membership_status", "('active', 'inactive')"),
        ("business_status", "('active', 'inactive')"),
        ("branch_status", "('open', 'closed')"),
        ("availability_slot_status", "('Open', 'Held', 'Booked', 'Blocked')"),
        ("booking_status", "('Active', 'PendingDeposit', 'CustomerCancelled', 'AdminCancelled', 'CheckedIn', 'Completed', 'NoShow', 'Expired')"),
        ("source_channel", "('LINE', 'PHONE', 'ADMIN')"),
        ("actor_type", "('Customer', 'Agent', 'Admin', 'System')"),
        ("availability_rule_effect", "('BLOCK')"),
        ("payment_provider", "('PromptPay', 'TrueMoney', 'Card', 'Stripe', 'Omise')"),
        ("payment_setting_status", "('active', 'inactive')"),
        ("payment_intent_status", "('Created', 'Pending', 'Succeeded', 'Failed', 'Expired', 'Refunded')"),
        ("payment_tx_status", "('Succeeded', 'Failed', 'Refunded')"),
        ("notification_channel", "('LINE', 'SMS', 'EMAIL')"),
        ("notification_job_status", "('Queued', 'Sent', 'Failed', 'Cancelled')"),
        ("line_connection_status", "('connected', 'disconnected')"),
        ("conversation_channel", "('LINE', 'PHONE', 'WEB')"),
        ("message_direction", "('inbound', 'outbound')"),
        ("admin_identifier_type", "('LINE', 'OAUTH')"),
        ("user_identifier_type", "('LINE', 'PHONE', 'OAUTH')"),
        ("booking_event_type", "('Created', 'SentToCustomer', 'CustomerConfirmed', 'Revised', 'Cancelled', 'CheckedIn', 'Completed', 'NoShow', 'DepositRequested', 'DepositPaid', 'Expired')"),
        ("notification_template", "('BookingCreated', 'NeedsConfirmation', 'Confirmed', 'Reminder24h', 'Reminder2h', 'Cancelled', 'DepositRequest', 'DepositReceived')"),
    ]
    
    for enum_name, enum_values in enum_definitions:
        op.execute(f"DO $$ BEGIN CREATE TYPE {enum_name} AS ENUM {enum_values}; EXCEPTION WHEN duplicate_object THEN null; END $$;")

    # Define enum types for use in table columns (with create_type=False to prevent auto-creation)
    # Since we've already created them above, SQLAlchemy should detect they exist
    record_status = postgresql.ENUM("active", "blocked", "deleted", name="record_status", create_type=False)
    membership_role = postgresql.ENUM("Owner", "Admin", "Staff", "Viewer", name="membership_role", create_type=False)
    membership_status = postgresql.ENUM("active", "inactive", name="membership_status", create_type=False)
    business_status = postgresql.ENUM("active", "inactive", name="business_status", create_type=False)
    branch_status = postgresql.ENUM("open", "closed", name="branch_status", create_type=False)
    availability_slot_status = postgresql.ENUM("Open", "Held", "Booked", "Blocked", name="availability_slot_status", create_type=False)
    booking_status = postgresql.ENUM(
        "Active",
        "PendingDeposit",
        "CustomerCancelled",
        "AdminCancelled",
        "CheckedIn",
        "Completed",
        "NoShow",
        "Expired",
        name="booking_status",
        create_type=False,
    )
    source_channel = postgresql.ENUM("LINE", "PHONE", "ADMIN", name="source_channel", create_type=False)
    actor_type = postgresql.ENUM("Customer", "Agent", "Admin", "System", name="actor_type", create_type=False)
    availability_rule_effect = postgresql.ENUM("BLOCK", name="availability_rule_effect", create_type=False)
    payment_provider = postgresql.ENUM("PromptPay", "TrueMoney", "Card", "Stripe", "Omise", name="payment_provider", create_type=False)
    payment_setting_status = postgresql.ENUM("active", "inactive", name="payment_setting_status", create_type=False)
    payment_intent_status = postgresql.ENUM(
        "Created",
        "Pending",
        "Succeeded",
        "Failed",
        "Expired",
        "Refunded",
        name="payment_intent_status",
        create_type=False,
    )
    payment_tx_status = postgresql.ENUM("Succeeded", "Failed", "Refunded", name="payment_tx_status", create_type=False)
    notification_channel = postgresql.ENUM("LINE", "SMS", "EMAIL", name="notification_channel", create_type=False)
    notification_job_status = postgresql.ENUM("Queued", "Sent", "Failed", "Cancelled", name="notification_job_status", create_type=False)
    line_connection_status = postgresql.ENUM("connected", "disconnected", name="line_connection_status", create_type=False)
    conversation_channel = postgresql.ENUM("LINE", "PHONE", "WEB", name="conversation_channel", create_type=False)
    message_direction = postgresql.ENUM("inbound", "outbound", name="message_direction", create_type=False)
    admin_identifier_type = postgresql.ENUM("LINE", "OAUTH", name="admin_identifier_type", create_type=False)
    user_identifier_type = postgresql.ENUM("LINE", "PHONE", "OAUTH", name="user_identifier_type", create_type=False)
    booking_event_type = postgresql.ENUM(
        "Created",
        "SentToCustomer",
        "CustomerConfirmed",
        "Revised",
        "Cancelled",
        "CheckedIn",
        "Completed",
        "NoShow",
        "DepositRequested",
        "DepositPaid",
        "Expired",
        name="booking_event_type",
        create_type=False,
    )
    notification_template = postgresql.ENUM(
        "BookingCreated",
        "NeedsConfirmation",
        "Confirmed",
        "Reminder24h",
        "Reminder2h",
        "Cancelled",
        "DepositRequest",
        "DepositReceived",
        name="notification_template",
        create_type=False,
    )

    op.create_table(
        "admin_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.Text(), nullable=False, unique=True),
        sa.Column("telno", sa.Text(), unique=True),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("status", record_status, nullable=False, server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "admin_identifiers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "admin_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("admin_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", admin_identifier_type, nullable=False),
        sa.Column("identifier", sa.Text(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("verified_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("status", record_status, nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("type", "identifier", name="admin_identifiers_type_identifier_uniq"),
    )
    op.create_index("idx_admin_identifiers_admin_id", "admin_identifiers", ["admin_id"])

    op.create_table(
        "businesses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("business_type", sa.Text(), nullable=False),
        sa.Column("timezone", sa.Text(), nullable=False, server_default="Asia/Bangkok"),
        sa.Column("location", sa.Text()),
        sa.Column("logo_url", sa.Text()),
        sa.Column("status", business_status, nullable=False, server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("location", sa.Text()),
        sa.Column("tel_no", sa.Text()),
        sa.Column("status", branch_status, nullable=False, server_default="open"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_branches_business_status", "branches", ["business_id", "status"])

    op.create_table(
        "services",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("price_amount", sa.Numeric()),
        sa.Column("price_currency", sa.Text()),
        sa.Column("deposit_required", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("deposit_amount", sa.Numeric()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("duration_minutes > 0", name="services_duration_minutes_chk"),
        sa.CheckConstraint("business_id IS NOT NULL", name="services_branch_business_match_chk"),
    )
    op.create_index("idx_services_business_active", "services", ["business_id", "active"])
    op.create_index("idx_services_branch", "services", ["branch_id"])

    op.create_table(
        "business_memberships",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "admin_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("admin_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("role", membership_role, nullable=False),
        sa.Column("status", membership_status, nullable=False, server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("business_id", "admin_user_id", name="business_memberships_uniq"),
    )
    op.create_index("idx_business_memberships_admin", "business_memberships", ["admin_user_id"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("status", record_status, nullable=False, server_default="active"),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "customer_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("display_name", sa.Text()),
        sa.Column("telno", sa.Text()),
        sa.Column("line_user_id", sa.Text()),
        sa.Column("notes", sa.Text()),
        sa.Column("locale", sa.Text()),
        sa.Column("timezone", sa.Text()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("business_id", "user_id", name="customer_profiles_business_user_uniq"),
    )
    op.create_index(
        "idx_customer_profiles_business_telno",
        "customer_profiles",
        ["business_id", "telno"],
        unique=True,
    )
    op.create_index(
        "idx_customer_profiles_business_line",
        "customer_profiles",
        ["business_id", "line_user_id"],
        unique=True,
    )
    op.create_index("idx_customer_profiles_user", "customer_profiles", ["user_id"])

    op.create_table(
        "user_identifiers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customer_profiles.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", user_identifier_type, nullable=False),
        sa.Column("identifier", sa.Text(), nullable=False),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("verified_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("status", record_status, nullable=False, server_default="active"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint(
            "business_id",
            "type",
            "identifier",
            name="user_identifiers_business_type_identifier_uniq",
        ),
    )
    op.create_index("idx_user_identifiers_customer", "user_identifiers", ["customer_id"])

    op.create_table(
        "weekly_availability_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("days_of_week", postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.Column("start_time_local", sa.Time(), nullable=False),
        sa.Column("end_time_local", sa.Time(), nullable=False),
        sa.Column("slot_interval_minutes", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("effective_from", sa.Date()),
        sa.Column("effective_to", sa.Date()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("slot_interval_minutes > 0", name="weekly_slot_interval_minutes_chk"),
        sa.CheckConstraint(
            "validate_days_of_week(days_of_week) = TRUE",
            name="weekly_days_valid_chk",
        ),
        sa.CheckConstraint("end_time_local > start_time_local", name="weekly_time_order_chk"),
    )
    op.create_index("idx_weekly_rules_branch_active", "weekly_availability_rules", ["branch_id", "active"])

    op.create_table(
        "datetime_availability_rules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("rule_effect", availability_rule_effect, nullable=False, server_default="BLOCK"),
        sa.Column("start_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("end_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("reason", sa.Text()),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_by_admin_user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("admin_profiles.id", ondelete="SET NULL"),
        ),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("end_at > start_at", name="datetime_time_order_chk"),
    )
    op.create_index("idx_datetime_rules_branch_active", "datetime_availability_rules", ["branch_id", "active"])
    op.create_index(
        "idx_datetime_rules_branch_timerange",
        "datetime_availability_rules",
        ["branch_id", "start_at", "end_at"],
    )

    op.create_table(
        "availability_slots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("branches.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("start_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("end_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", availability_slot_status, nullable=False, server_default="Open"),
        sa.Column("held_by_booking_id", postgresql.UUID(as_uuid=True)),
        sa.Column("hold_expires_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("capacity > 0", name="availability_slots_capacity_chk"),
        sa.CheckConstraint("end_at > start_at", name="availability_slots_time_order_chk"),
    )
    op.create_index("idx_availability_slots_branch_start", "availability_slots", ["branch_id", "start_at"])

    op.create_table(
        "bookings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "branch_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("branches.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "service_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("services.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customer_profiles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("booking_number", sa.Text(), nullable=False),
        sa.Column("start_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("end_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("status", booking_status, nullable=False, server_default="Active"),
        sa.Column("source_channel", source_channel, nullable=False),
        sa.Column("customer_note", sa.Text()),
        sa.Column("internal_note", sa.Text()),
        sa.Column("last_confirmed_version_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_by_type", actor_type, nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("cancelled_at", sa.TIMESTAMP(timezone=True)),
        sa.UniqueConstraint("business_id", "booking_number", name="bookings_business_booking_number_uniq"),
        sa.CheckConstraint("end_at > start_at", name="bookings_time_order_chk"),
    )
    op.create_index("idx_bookings_business_status_start", "bookings", ["business_id", "status", "start_at"])
    op.create_index("idx_bookings_customer_start", "bookings", ["customer_id", "start_at"])
    op.create_index("idx_bookings_branch_start", "bookings", ["branch_id", "start_at"])

    op.create_foreign_key(
        "availability_slots_held_by_booking_fk",
        "availability_slots",
        "bookings",
        ["held_by_booking_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "booking_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "booking_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("snapshot", postgresql.JSONB(), nullable=False),
        sa.Column("created_by_type", actor_type, nullable=False),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("booking_id", "version_number", name="booking_versions_uniq"),
        sa.CheckConstraint("version_number > 0", name="booking_versions_version_number_chk"),
    )
    op.create_index(
        "idx_booking_versions_booking_version_desc",
        "booking_versions",
        ["booking_id", sa.text("version_number DESC")],
    )

    op.create_foreign_key(
        "bookings_last_confirmed_version_fk",
        "bookings",
        "booking_versions",
        ["last_confirmed_version_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "booking_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "booking_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("event_type", booking_event_type, nullable=False),
        sa.Column("actor_type", actor_type, nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True)),
        sa.Column("payload", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_booking_events_booking_created", "booking_events", ["booking_id", "created_at"])

    op.create_table(
        "payment_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", payment_provider, nullable=False),
        sa.Column("status", payment_setting_status, nullable=False, server_default="active"),
        sa.Column("config", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("business_id", "provider", name="payment_settings_business_provider_uniq"),
    )

    op.create_table(
        "payment_intents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "booking_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bookings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("provider", payment_provider, nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.Column("currency", sa.Text(), nullable=False),
        sa.Column("status", payment_intent_status, nullable=False, server_default="Created"),
        sa.Column("expires_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("provider_reference", sa.Text()),
        sa.Column("qr_payload", postgresql.JSONB()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint("amount >= 0", name="payment_intents_amount_chk"),
    )
    op.create_index("idx_payment_intents_booking", "payment_intents", ["booking_id"])
    op.create_index(
        "idx_payment_intents_business_status_created",
        "payment_intents",
        ["business_id", "status", "created_at"],
    )

    op.create_table(
        "payment_transactions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "payment_intent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("payment_intents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", payment_tx_status, nullable=False),
        sa.Column("provider_payload", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("processed_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_payment_transactions_intent_created",
        "payment_transactions",
        ["payment_intent_id", "created_at"],
    )

    op.create_table(
        "notification_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "booking_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bookings.id", ondelete="CASCADE"),
        ),
        sa.Column("channel", notification_channel, nullable=False),
        sa.Column("template", notification_template, nullable=False),
        sa.Column("scheduled_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("sent_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("status", notification_job_status, nullable=False, server_default="Queued"),
        sa.Column("provider_reference", sa.Text()),
        sa.Column("payload", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_notification_jobs_business_status_scheduled",
        "notification_jobs",
        ["business_id", "status", "scheduled_at"],
    )
    op.create_index("idx_notification_jobs_booking", "notification_jobs", ["booking_id"])

    op.create_table(
        "line_oa_connections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel_id", sa.Text(), nullable=False),
        sa.Column("channel_secret", sa.Text(), nullable=False),
        sa.Column("channel_access_token", sa.Text(), nullable=False),
        sa.Column("bot_destination_id", sa.Text()),
        sa.Column("liff_id", sa.Text()),
        sa.Column("login_channel_id", sa.Text()),
        sa.Column("login_channel_access_token", sa.Text()),
        sa.Column("connected_status", line_connection_status, nullable=False, server_default="disconnected"),
        sa.Column("webhook_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("config", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("business_id", name="line_oa_connections_business_uniq"),
    )

    op.create_table(
        "conversations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customer_profiles.id", ondelete="SET NULL"),
        ),
        sa.Column("channel", conversation_channel, nullable=False),
        sa.Column("external_thread_id", sa.Text()),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("idx_conversations_business_customer", "conversations", ["business_id", "customer_id"])

    op.create_table(
        "conversation_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("direction", message_direction, nullable=False),
        sa.Column("sender_type", actor_type, nullable=False),
        sa.Column("sender_id", postgresql.UUID(as_uuid=True)),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index(
        "idx_conversation_messages_conversation_created",
        "conversation_messages",
        ["conversation_id", "created_at"],
    )

    op.create_table(
        "call_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "business_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("businesses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "customer_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("customer_profiles.id", ondelete="SET NULL"),
        ),
        sa.Column("provider", sa.Text(), nullable=False, server_default="Twilio"),
        sa.Column("provider_call_id", sa.Text()),
        sa.Column("started_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("ended_at", sa.TIMESTAMP(timezone=True)),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.CheckConstraint(
            "ended_at IS NULL OR ended_at >= started_at",
            name="call_sessions_time_order_chk",
        ),
    )
    op.create_index("idx_call_sessions_business_started", "call_sessions", ["business_id", "started_at"])


def downgrade() -> None:
    op.drop_index("idx_call_sessions_business_started", table_name="call_sessions")
    op.drop_table("call_sessions")

    op.drop_index("idx_conversation_messages_conversation_created", table_name="conversation_messages")
    op.drop_table("conversation_messages")

    op.drop_index("idx_conversations_business_customer", table_name="conversations")
    op.drop_table("conversations")

    op.drop_table("line_oa_connections")

    op.drop_index("idx_notification_jobs_booking", table_name="notification_jobs")
    op.drop_index("idx_notification_jobs_business_status_scheduled", table_name="notification_jobs")
    op.drop_table("notification_jobs")

    op.drop_index("idx_payment_transactions_intent_created", table_name="payment_transactions")
    op.drop_table("payment_transactions")

    op.drop_index("idx_payment_intents_business_status_created", table_name="payment_intents")
    op.drop_index("idx_payment_intents_booking", table_name="payment_intents")
    op.drop_table("payment_intents")

    op.drop_table("payment_settings")

    op.drop_index("idx_booking_events_booking_created", table_name="booking_events")
    op.drop_table("booking_events")

    op.drop_constraint("bookings_last_confirmed_version_fk", "bookings", type_="foreignkey")
    op.drop_index("idx_booking_versions_booking_version_desc", table_name="booking_versions")
    op.drop_table("booking_versions")

    op.drop_constraint("availability_slots_held_by_booking_fk", "availability_slots", type_="foreignkey")
    op.drop_index("idx_bookings_branch_start", table_name="bookings")
    op.drop_index("idx_bookings_customer_start", table_name="bookings")
    op.drop_index("idx_bookings_business_status_start", table_name="bookings")
    op.drop_table("bookings")

    op.drop_index("idx_availability_slots_branch_start", table_name="availability_slots")
    op.drop_table("availability_slots")

    op.drop_index("idx_datetime_rules_branch_timerange", table_name="datetime_availability_rules")
    op.drop_index("idx_datetime_rules_branch_active", table_name="datetime_availability_rules")
    op.drop_table("datetime_availability_rules")

    op.drop_index("idx_weekly_rules_branch_active", table_name="weekly_availability_rules")
    op.drop_table("weekly_availability_rules")

    op.drop_index("idx_user_identifiers_customer", table_name="user_identifiers")
    op.drop_table("user_identifiers")

    op.drop_index("idx_customer_profiles_user", table_name="customer_profiles")
    op.drop_index("idx_customer_profiles_business_line", table_name="customer_profiles")
    op.drop_index("idx_customer_profiles_business_telno", table_name="customer_profiles")
    op.drop_table("customer_profiles")

    op.drop_table("users")

    op.drop_index("idx_business_memberships_admin", table_name="business_memberships")
    op.drop_table("business_memberships")

    op.drop_index("idx_services_branch", table_name="services")
    op.drop_index("idx_services_business_active", table_name="services")
    op.drop_table("services")

    op.drop_index("idx_branches_business_status", table_name="branches")
    op.drop_table("branches")

    op.drop_table("businesses")

    op.drop_index("idx_admin_identifiers_admin_id", table_name="admin_identifiers")
    op.drop_table("admin_identifiers")

    op.drop_table("admin_profiles")

    bind = op.get_bind()
    for enum_name in (
        "notification_template",
        "booking_event_type",
        "user_identifier_type",
        "admin_identifier_type",
        "message_direction",
        "conversation_channel",
        "line_connection_status",
        "notification_job_status",
        "notification_channel",
        "payment_tx_status",
        "payment_intent_status",
        "payment_setting_status",
        "payment_provider",
        "availability_rule_effect",
        "actor_type",
        "source_channel",
        "booking_status",
        "availability_slot_status",
        "branch_status",
        "business_status",
        "membership_status",
        "membership_role",
        "record_status",
    ):
        sa.Enum(name=enum_name).drop(bind, checkfirst=True)

    op.execute("DROP EXTENSION IF EXISTS pgcrypto;")
