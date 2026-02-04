-- -------------------------------------------------------------
-- TablePlus 6.8.0(654)
--
-- https://tableplus.com/
--
-- Database: ai-appointment
-- Generation Time: 2026-02-02 09:20:07.2220
-- -------------------------------------------------------------


DROP TABLE IF EXISTS "public"."user";
-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS user_id_seq;

-- Table Definition
CREATE TABLE "public"."user" (
    "created_at" timestamp NOT NULL,
    "id" int4 NOT NULL DEFAULT nextval('user_id_seq'::regclass),
    "email" varchar NOT NULL,
    "hashed_password" varchar NOT NULL,
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."session";
-- Table Definition
CREATE TABLE "public"."session" (
    "created_at" timestamp NOT NULL,
    "id" varchar NOT NULL,
    "user_id" int4 NOT NULL,
    "name" varchar NOT NULL,
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."alembic_version";
-- Table Definition
CREATE TABLE "public"."alembic_version" (
    "version_num" varchar(32) NOT NULL,
    PRIMARY KEY ("version_num")
);

DROP TABLE IF EXISTS "public"."admin_profiles";
DROP TYPE IF EXISTS "public"."record_status";
CREATE TYPE "public"."record_status" AS ENUM ('active', 'blocked', 'deleted');

-- Table Definition
CREATE TABLE "public"."admin_profiles" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "email" text NOT NULL,
    "telno" text,
    "name" text NOT NULL,
    "status" "public"."record_status" NOT NULL DEFAULT 'active'::record_status,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."admin_identifiers";
DROP TYPE IF EXISTS "public"."admin_identifier_type";
CREATE TYPE "public"."admin_identifier_type" AS ENUM ('LINE', 'OAUTH');
DROP TYPE IF EXISTS "public"."record_status";
CREATE TYPE "public"."record_status" AS ENUM ('active', 'blocked', 'deleted');

-- Table Definition
CREATE TABLE "public"."admin_identifiers" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "admin_id" uuid NOT NULL,
    "type" "public"."admin_identifier_type" NOT NULL,
    "identifier" text NOT NULL,
    "is_verified" bool NOT NULL DEFAULT false,
    "verified_at" timestamptz,
    "status" "public"."record_status" NOT NULL DEFAULT 'active'::record_status,
    "metadata" jsonb NOT NULL DEFAULT '{}'::jsonb,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."businesses";
DROP TYPE IF EXISTS "public"."business_status";
CREATE TYPE "public"."business_status" AS ENUM ('active', 'inactive');

-- Table Definition
CREATE TABLE "public"."businesses" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "name" text NOT NULL,
    "business_type" text NOT NULL,
    "timezone" text NOT NULL DEFAULT 'Asia/Bangkok'::text,
    "location" text,
    "logo_url" text,
    "status" "public"."business_status" NOT NULL DEFAULT 'active'::business_status,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."branches";
DROP TYPE IF EXISTS "public"."branch_status";
CREATE TYPE "public"."branch_status" AS ENUM ('open', 'closed');

-- Table Definition
CREATE TABLE "public"."branches" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "name" text NOT NULL,
    "location" text,
    "tel_no" text,
    "status" "public"."branch_status" NOT NULL DEFAULT 'open'::branch_status,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."services";
-- Table Definition
CREATE TABLE "public"."services" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "branch_id" uuid NOT NULL,
    "business_id" uuid NOT NULL CHECK (business_id IS NOT NULL),
    "name" text NOT NULL,
    "duration_minutes" int4 NOT NULL CHECK (duration_minutes > 0),
    "price_amount" numeric,
    "price_currency" text,
    "deposit_required" bool NOT NULL DEFAULT false,
    "deposit_amount" numeric,
    "active" bool NOT NULL DEFAULT true,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."business_memberships";
DROP TYPE IF EXISTS "public"."membership_role";
CREATE TYPE "public"."membership_role" AS ENUM ('Owner', 'Admin', 'Staff', 'Viewer');
DROP TYPE IF EXISTS "public"."membership_status";
CREATE TYPE "public"."membership_status" AS ENUM ('active', 'inactive');

-- Table Definition
CREATE TABLE "public"."business_memberships" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "admin_user_id" uuid NOT NULL,
    "role" "public"."membership_role" NOT NULL,
    "status" "public"."membership_status" NOT NULL DEFAULT 'active'::membership_status,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."customer_profiles";
-- Table Definition
CREATE TABLE "public"."customer_profiles" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "user_id" uuid NOT NULL,
    "display_name" text,
    "telno" text,
    "line_user_id" text,
    "notes" text,
    "locale" text,
    "timezone" text,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."users";
DROP TYPE IF EXISTS "public"."record_status";
CREATE TYPE "public"."record_status" AS ENUM ('active', 'blocked', 'deleted');

-- Table Definition
CREATE TABLE "public"."users" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "status" "public"."record_status" NOT NULL DEFAULT 'active'::record_status,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."user_identifiers";
DROP TYPE IF EXISTS "public"."user_identifier_type";
CREATE TYPE "public"."user_identifier_type" AS ENUM ('LINE', 'PHONE', 'OAUTH');
DROP TYPE IF EXISTS "public"."record_status";
CREATE TYPE "public"."record_status" AS ENUM ('active', 'blocked', 'deleted');

-- Table Definition
CREATE TABLE "public"."user_identifiers" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "customer_id" uuid NOT NULL,
    "business_id" uuid NOT NULL,
    "type" "public"."user_identifier_type" NOT NULL,
    "identifier" text NOT NULL,
    "is_verified" bool NOT NULL DEFAULT false,
    "verified_at" timestamptz,
    "status" "public"."record_status" NOT NULL DEFAULT 'active'::record_status,
    "metadata" jsonb NOT NULL DEFAULT '{}'::jsonb,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."weekly_availability_rules";
-- Table Definition
CREATE TABLE "public"."weekly_availability_rules" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "branch_id" uuid NOT NULL,
    "name" text NOT NULL,
    "days_of_week" _int4 NOT NULL CHECK (validate_days_of_week(days_of_week) = true),
    "start_time_local" time NOT NULL,
    "end_time_local" time NOT NULL,
    "slot_interval_minutes" int4 NOT NULL CHECK (slot_interval_minutes > 0),
    "active" bool NOT NULL DEFAULT true,
    "effective_from" date,
    "effective_to" date,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."datetime_availability_rules";
DROP TYPE IF EXISTS "public"."availability_rule_effect";
CREATE TYPE "public"."availability_rule_effect" AS ENUM ('BLOCK');

-- Table Definition
CREATE TABLE "public"."datetime_availability_rules" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "branch_id" uuid NOT NULL,
    "name" text NOT NULL,
    "rule_effect" "public"."availability_rule_effect" NOT NULL DEFAULT 'BLOCK'::availability_rule_effect,
    "start_at" timestamptz NOT NULL,
    "end_at" timestamptz NOT NULL,
    "priority" int4 NOT NULL DEFAULT 100,
    "reason" text,
    "active" bool NOT NULL DEFAULT true,
    "created_by_admin_user_id" uuid,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."availability_slots";
DROP TYPE IF EXISTS "public"."availability_slot_status";
CREATE TYPE "public"."availability_slot_status" AS ENUM ('Open', 'Held', 'Booked', 'Blocked');

-- Table Definition
CREATE TABLE "public"."availability_slots" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "branch_id" uuid NOT NULL,
    "start_at" timestamptz NOT NULL,
    "end_at" timestamptz NOT NULL,
    "capacity" int4 NOT NULL DEFAULT 1 CHECK (capacity > 0),
    "status" "public"."availability_slot_status" NOT NULL DEFAULT 'Open'::availability_slot_status,
    "held_by_booking_id" uuid,
    "hold_expires_at" timestamptz,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."bookings";
DROP TYPE IF EXISTS "public"."booking_status";
CREATE TYPE "public"."booking_status" AS ENUM ('Active', 'PendingDeposit', 'CustomerCancelled', 'AdminCancelled', 'CheckedIn', 'Completed', 'NoShow', 'Expired');
DROP TYPE IF EXISTS "public"."source_channel";
CREATE TYPE "public"."source_channel" AS ENUM ('LINE', 'PHONE', 'ADMIN');
DROP TYPE IF EXISTS "public"."actor_type";
CREATE TYPE "public"."actor_type" AS ENUM ('Customer', 'Agent', 'Admin', 'System');

-- Table Definition
CREATE TABLE "public"."bookings" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "branch_id" uuid NOT NULL,
    "service_id" uuid NOT NULL,
    "customer_id" uuid NOT NULL,
    "booking_number" text NOT NULL,
    "start_at" timestamptz NOT NULL,
    "end_at" timestamptz NOT NULL,
    "status" "public"."booking_status" NOT NULL DEFAULT 'Active'::booking_status,
    "source_channel" "public"."source_channel" NOT NULL,
    "customer_note" text,
    "internal_note" text,
    "last_confirmed_version_id" uuid,
    "created_by_type" "public"."actor_type" NOT NULL,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    "cancelled_at" timestamptz,
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."booking_versions";
DROP TYPE IF EXISTS "public"."actor_type";
CREATE TYPE "public"."actor_type" AS ENUM ('Customer', 'Agent', 'Admin', 'System');

-- Table Definition
CREATE TABLE "public"."booking_versions" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "booking_id" uuid NOT NULL,
    "version_number" int4 NOT NULL CHECK (version_number > 0),
    "snapshot" jsonb NOT NULL,
    "created_by_type" "public"."actor_type" NOT NULL,
    "created_by_id" uuid,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."booking_events";
DROP TYPE IF EXISTS "public"."booking_event_type";
CREATE TYPE "public"."booking_event_type" AS ENUM ('Created', 'SentToCustomer', 'CustomerConfirmed', 'Revised', 'Cancelled', 'CheckedIn', 'Completed', 'NoShow', 'DepositRequested', 'DepositPaid', 'Expired');
DROP TYPE IF EXISTS "public"."actor_type";
CREATE TYPE "public"."actor_type" AS ENUM ('Customer', 'Agent', 'Admin', 'System');

-- Table Definition
CREATE TABLE "public"."booking_events" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "booking_id" uuid NOT NULL,
    "event_type" "public"."booking_event_type" NOT NULL,
    "actor_type" "public"."actor_type" NOT NULL,
    "actor_id" uuid,
    "payload" jsonb NOT NULL DEFAULT '{}'::jsonb,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."payment_settings";
DROP TYPE IF EXISTS "public"."payment_provider";
CREATE TYPE "public"."payment_provider" AS ENUM ('PromptPay', 'TrueMoney', 'Card', 'Stripe', 'Omise');
DROP TYPE IF EXISTS "public"."payment_setting_status";
CREATE TYPE "public"."payment_setting_status" AS ENUM ('active', 'inactive');

-- Table Definition
CREATE TABLE "public"."payment_settings" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "provider" "public"."payment_provider" NOT NULL,
    "status" "public"."payment_setting_status" NOT NULL DEFAULT 'active'::payment_setting_status,
    "config" jsonb NOT NULL DEFAULT '{}'::jsonb,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."payment_intents";
DROP TYPE IF EXISTS "public"."payment_provider";
CREATE TYPE "public"."payment_provider" AS ENUM ('PromptPay', 'TrueMoney', 'Card', 'Stripe', 'Omise');
DROP TYPE IF EXISTS "public"."payment_intent_status";
CREATE TYPE "public"."payment_intent_status" AS ENUM ('Created', 'Pending', 'Succeeded', 'Failed', 'Expired', 'Refunded');

-- Table Definition
CREATE TABLE "public"."payment_intents" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "booking_id" uuid NOT NULL,
    "provider" "public"."payment_provider" NOT NULL,
    "amount" numeric NOT NULL CHECK (amount >= (0)::numeric),
    "currency" text NOT NULL,
    "status" "public"."payment_intent_status" NOT NULL DEFAULT 'Created'::payment_intent_status,
    "expires_at" timestamptz,
    "provider_reference" text,
    "qr_payload" jsonb,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."payment_transactions";
DROP TYPE IF EXISTS "public"."payment_tx_status";
CREATE TYPE "public"."payment_tx_status" AS ENUM ('Succeeded', 'Failed', 'Refunded');

-- Table Definition
CREATE TABLE "public"."payment_transactions" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "payment_intent_id" uuid NOT NULL,
    "status" "public"."payment_tx_status" NOT NULL,
    "provider_payload" jsonb NOT NULL DEFAULT '{}'::jsonb,
    "processed_at" timestamptz,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."notification_jobs";
DROP TYPE IF EXISTS "public"."notification_channel";
CREATE TYPE "public"."notification_channel" AS ENUM ('LINE', 'SMS', 'EMAIL');
DROP TYPE IF EXISTS "public"."notification_template";
CREATE TYPE "public"."notification_template" AS ENUM ('BookingCreated', 'NeedsConfirmation', 'Confirmed', 'Reminder24h', 'Reminder2h', 'Cancelled', 'DepositRequest', 'DepositReceived');
DROP TYPE IF EXISTS "public"."notification_job_status";
CREATE TYPE "public"."notification_job_status" AS ENUM ('Queued', 'Sent', 'Failed', 'Cancelled');

-- Table Definition
CREATE TABLE "public"."notification_jobs" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "booking_id" uuid,
    "channel" "public"."notification_channel" NOT NULL,
    "template" "public"."notification_template" NOT NULL,
    "scheduled_at" timestamptz NOT NULL,
    "sent_at" timestamptz,
    "status" "public"."notification_job_status" NOT NULL DEFAULT 'Queued'::notification_job_status,
    "provider_reference" text,
    "payload" jsonb NOT NULL DEFAULT '{}'::jsonb,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."line_oa_connections";
DROP TYPE IF EXISTS "public"."line_connection_status";
CREATE TYPE "public"."line_connection_status" AS ENUM ('connected', 'disconnected');

-- Table Definition
CREATE TABLE "public"."line_oa_connections" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "channel_id" text NOT NULL,
    "channel_secret" text NOT NULL,
    "channel_access_token" text NOT NULL,
    "bot_destination_id" text,
    "liff_id" text,
    "login_channel_id" text,
    "login_channel_access_token" text,
    "connected_status" "public"."line_connection_status" NOT NULL DEFAULT 'disconnected'::line_connection_status,
    "webhook_verified" bool NOT NULL DEFAULT false,
    "config" jsonb NOT NULL DEFAULT '{}'::jsonb,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."conversations";
DROP TYPE IF EXISTS "public"."conversation_channel";
CREATE TYPE "public"."conversation_channel" AS ENUM ('LINE', 'PHONE', 'WEB');

-- Table Definition
CREATE TABLE "public"."conversations" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "customer_id" uuid,
    "channel" "public"."conversation_channel" NOT NULL,
    "external_thread_id" text,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    "updated_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."conversation_messages";
DROP TYPE IF EXISTS "public"."message_direction";
CREATE TYPE "public"."message_direction" AS ENUM ('inbound', 'outbound');
DROP TYPE IF EXISTS "public"."actor_type";
CREATE TYPE "public"."actor_type" AS ENUM ('Customer', 'Agent', 'Admin', 'System');

-- Table Definition
CREATE TABLE "public"."conversation_messages" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "conversation_id" uuid NOT NULL,
    "direction" "public"."message_direction" NOT NULL,
    "sender_type" "public"."actor_type" NOT NULL,
    "sender_id" uuid,
    "content" text NOT NULL,
    "metadata" jsonb NOT NULL DEFAULT '{}'::jsonb,
    "created_at" timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);

DROP TABLE IF EXISTS "public"."call_sessions";
-- Table Definition
CREATE TABLE "public"."call_sessions" (
    "id" uuid NOT NULL DEFAULT gen_random_uuid(),
    "business_id" uuid NOT NULL,
    "customer_id" uuid,
    "provider" text NOT NULL DEFAULT 'Twilio'::text,
    "provider_call_id" text,
    "started_at" timestamptz NOT NULL DEFAULT now(),
    "ended_at" timestamptz,
    "metadata" jsonb NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY ("id")
);

INSERT INTO "public"."alembic_version" ("version_num") VALUES
('20260201_000001');



-- Indices
CREATE UNIQUE INDEX ix_user_email ON public."user" USING btree (email);
ALTER TABLE "public"."session" ADD FOREIGN KEY ("user_id") REFERENCES "public"."user"("id");


-- Indices
CREATE UNIQUE INDEX alembic_version_pkc ON public.alembic_version USING btree (version_num);


-- Indices
CREATE UNIQUE INDEX admin_profiles_email_key ON public.admin_profiles USING btree (email);
CREATE UNIQUE INDEX admin_profiles_telno_key ON public.admin_profiles USING btree (telno);
ALTER TABLE "public"."admin_identifiers" ADD FOREIGN KEY ("admin_id") REFERENCES "public"."admin_profiles"("id") ON DELETE CASCADE;


-- Indices
CREATE UNIQUE INDEX admin_identifiers_type_identifier_uniq ON public.admin_identifiers USING btree (type, identifier);
CREATE INDEX idx_admin_identifiers_admin_id ON public.admin_identifiers USING btree (admin_id);
ALTER TABLE "public"."branches" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;


-- Indices
CREATE INDEX idx_branches_business_status ON public.branches USING btree (business_id, status);
ALTER TABLE "public"."services" ADD FOREIGN KEY ("branch_id") REFERENCES "public"."branches"("id") ON DELETE CASCADE;
ALTER TABLE "public"."services" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;


-- Indices
CREATE INDEX idx_services_business_active ON public.services USING btree (business_id, active);
CREATE INDEX idx_services_branch ON public.services USING btree (branch_id);
ALTER TABLE "public"."business_memberships" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;
ALTER TABLE "public"."business_memberships" ADD FOREIGN KEY ("admin_user_id") REFERENCES "public"."admin_profiles"("id") ON DELETE CASCADE;


-- Indices
CREATE UNIQUE INDEX business_memberships_uniq ON public.business_memberships USING btree (business_id, admin_user_id);
CREATE INDEX idx_business_memberships_admin ON public.business_memberships USING btree (admin_user_id);
ALTER TABLE "public"."customer_profiles" ADD FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;
ALTER TABLE "public"."customer_profiles" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;


-- Indices
CREATE UNIQUE INDEX customer_profiles_business_user_uniq ON public.customer_profiles USING btree (business_id, user_id);
CREATE UNIQUE INDEX idx_customer_profiles_business_telno ON public.customer_profiles USING btree (business_id, telno);
CREATE UNIQUE INDEX idx_customer_profiles_business_line ON public.customer_profiles USING btree (business_id, line_user_id);
CREATE INDEX idx_customer_profiles_user ON public.customer_profiles USING btree (user_id);
ALTER TABLE "public"."user_identifiers" ADD FOREIGN KEY ("customer_id") REFERENCES "public"."customer_profiles"("id") ON DELETE CASCADE;
ALTER TABLE "public"."user_identifiers" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;


-- Indices
CREATE UNIQUE INDEX user_identifiers_business_type_identifier_uniq ON public.user_identifiers USING btree (business_id, type, identifier);
CREATE INDEX idx_user_identifiers_customer ON public.user_identifiers USING btree (customer_id);
ALTER TABLE "public"."weekly_availability_rules" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;
ALTER TABLE "public"."weekly_availability_rules" ADD FOREIGN KEY ("branch_id") REFERENCES "public"."branches"("id") ON DELETE CASCADE;


-- Indices
CREATE INDEX idx_weekly_rules_branch_active ON public.weekly_availability_rules USING btree (branch_id, active);
ALTER TABLE "public"."datetime_availability_rules" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;
ALTER TABLE "public"."datetime_availability_rules" ADD FOREIGN KEY ("branch_id") REFERENCES "public"."branches"("id") ON DELETE CASCADE;
ALTER TABLE "public"."datetime_availability_rules" ADD FOREIGN KEY ("created_by_admin_user_id") REFERENCES "public"."admin_profiles"("id") ON DELETE SET NULL;


-- Indices
CREATE INDEX idx_datetime_rules_branch_active ON public.datetime_availability_rules USING btree (branch_id, active);
CREATE INDEX idx_datetime_rules_branch_timerange ON public.datetime_availability_rules USING btree (branch_id, start_at, end_at);
ALTER TABLE "public"."availability_slots" ADD FOREIGN KEY ("branch_id") REFERENCES "public"."branches"("id") ON DELETE CASCADE;
ALTER TABLE "public"."availability_slots" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;
ALTER TABLE "public"."availability_slots" ADD FOREIGN KEY ("held_by_booking_id") REFERENCES "public"."bookings"("id") ON DELETE SET NULL;


-- Indices
CREATE INDEX idx_availability_slots_branch_start ON public.availability_slots USING btree (branch_id, start_at);
ALTER TABLE "public"."bookings" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;
ALTER TABLE "public"."bookings" ADD FOREIGN KEY ("customer_id") REFERENCES "public"."customer_profiles"("id") ON DELETE RESTRICT;
ALTER TABLE "public"."bookings" ADD FOREIGN KEY ("service_id") REFERENCES "public"."services"("id") ON DELETE RESTRICT;
ALTER TABLE "public"."bookings" ADD FOREIGN KEY ("last_confirmed_version_id") REFERENCES "public"."booking_versions"("id") ON DELETE SET NULL;
ALTER TABLE "public"."bookings" ADD FOREIGN KEY ("branch_id") REFERENCES "public"."branches"("id") ON DELETE RESTRICT;


-- Indices
CREATE UNIQUE INDEX bookings_business_booking_number_uniq ON public.bookings USING btree (business_id, booking_number);
CREATE INDEX idx_bookings_business_status_start ON public.bookings USING btree (business_id, status, start_at);
CREATE INDEX idx_bookings_customer_start ON public.bookings USING btree (customer_id, start_at);
CREATE INDEX idx_bookings_branch_start ON public.bookings USING btree (branch_id, start_at);
ALTER TABLE "public"."booking_versions" ADD FOREIGN KEY ("booking_id") REFERENCES "public"."bookings"("id") ON DELETE CASCADE;


-- Indices
CREATE UNIQUE INDEX booking_versions_uniq ON public.booking_versions USING btree (booking_id, version_number);
CREATE INDEX idx_booking_versions_booking_version_desc ON public.booking_versions USING btree (booking_id, version_number DESC);
ALTER TABLE "public"."booking_events" ADD FOREIGN KEY ("booking_id") REFERENCES "public"."bookings"("id") ON DELETE CASCADE;


-- Indices
CREATE INDEX idx_booking_events_booking_created ON public.booking_events USING btree (booking_id, created_at);
ALTER TABLE "public"."payment_settings" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;


-- Indices
CREATE UNIQUE INDEX payment_settings_business_provider_uniq ON public.payment_settings USING btree (business_id, provider);
ALTER TABLE "public"."payment_intents" ADD FOREIGN KEY ("booking_id") REFERENCES "public"."bookings"("id") ON DELETE CASCADE;
ALTER TABLE "public"."payment_intents" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;


-- Indices
CREATE INDEX idx_payment_intents_booking ON public.payment_intents USING btree (booking_id);
CREATE INDEX idx_payment_intents_business_status_created ON public.payment_intents USING btree (business_id, status, created_at);
ALTER TABLE "public"."payment_transactions" ADD FOREIGN KEY ("payment_intent_id") REFERENCES "public"."payment_intents"("id") ON DELETE CASCADE;


-- Indices
CREATE INDEX idx_payment_transactions_intent_created ON public.payment_transactions USING btree (payment_intent_id, created_at);
ALTER TABLE "public"."notification_jobs" ADD FOREIGN KEY ("booking_id") REFERENCES "public"."bookings"("id") ON DELETE CASCADE;
ALTER TABLE "public"."notification_jobs" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;


-- Indices
CREATE INDEX idx_notification_jobs_business_status_scheduled ON public.notification_jobs USING btree (business_id, status, scheduled_at);
CREATE INDEX idx_notification_jobs_booking ON public.notification_jobs USING btree (booking_id);
ALTER TABLE "public"."line_oa_connections" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;


-- Indices
CREATE UNIQUE INDEX line_oa_connections_business_uniq ON public.line_oa_connections USING btree (business_id);
ALTER TABLE "public"."conversations" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;
ALTER TABLE "public"."conversations" ADD FOREIGN KEY ("customer_id") REFERENCES "public"."customer_profiles"("id") ON DELETE SET NULL;


-- Indices
CREATE INDEX idx_conversations_business_customer ON public.conversations USING btree (business_id, customer_id);
ALTER TABLE "public"."conversation_messages" ADD FOREIGN KEY ("conversation_id") REFERENCES "public"."conversations"("id") ON DELETE CASCADE;


-- Indices
CREATE INDEX idx_conversation_messages_conversation_created ON public.conversation_messages USING btree (conversation_id, created_at);
ALTER TABLE "public"."call_sessions" ADD FOREIGN KEY ("customer_id") REFERENCES "public"."customer_profiles"("id") ON DELETE SET NULL;
ALTER TABLE "public"."call_sessions" ADD FOREIGN KEY ("business_id") REFERENCES "public"."businesses"("id") ON DELETE CASCADE;


-- Indices
CREATE INDEX idx_call_sessions_business_started ON public.call_sessions USING btree (business_id, started_at);
