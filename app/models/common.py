"""Shared helpers for appointment domain models."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(UTC)
