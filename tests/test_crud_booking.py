"""CRUD tests for booking endpoints."""

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_booking_crud(db_client):
    booking_payload = {
        "business_id": str(uuid4()),
        "branch_id": str(uuid4()),
        "service_id": str(uuid4()),
        "customer_id": str(uuid4()),
        "booking_number": "BK-2026-001",
        "start_at": "2026-02-15T10:00:00Z",
        "end_at": "2026-02-15T10:30:00Z",
        "status": "Active",
        "source_channel": "LINE",
        "customer_note": "Please arrive on time",
        "internal_note": None,
        "last_confirmed_version_id": None,
        "created_by_type": "Customer",
        "cancelled_at": None,
    }

    create_response = await db_client.post("/api/v1/crud/booking/bookings/", json=booking_payload)
    assert create_response.status_code == 201
    booking = create_response.json()
    booking_id = booking["id"]

    get_response = await db_client.get(f"/api/v1/crud/booking/bookings/{booking_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == booking_id

    update_response = await db_client.patch(
        f"/api/v1/crud/booking/bookings/{booking_id}",
        json={"status": "Completed"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Completed"

    delete_response = await db_client.delete(f"/api/v1/crud/booking/bookings/{booking_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_booking_versions_and_events(db_client):
    booking_response = await db_client.post(
        "/api/v1/crud/booking/bookings/",
        json={
            "business_id": str(uuid4()),
            "branch_id": str(uuid4()),
            "service_id": str(uuid4()),
            "customer_id": str(uuid4()),
            "booking_number": "BK-2026-002",
            "start_at": "2026-02-16T10:00:00Z",
            "end_at": "2026-02-16T10:30:00Z",
            "status": "Active",
            "source_channel": "LINE",
            "customer_note": None,
            "internal_note": None,
            "last_confirmed_version_id": None,
            "created_by_type": "Customer",
            "cancelled_at": None,
        },
    )

    booking_id = booking_response.json()["id"]

    version_response = await db_client.post(
        "/api/v1/crud/booking/versions/",
        json={
            "booking_id": booking_id,
            "version_number": 1,
            "snapshot": {"notes": "Initial"},
            "created_by_type": "Customer",
            "created_by_id": None,
        },
    )

    assert version_response.status_code == 201
    version_id = version_response.json()["id"]

    event_response = await db_client.post(
        "/api/v1/crud/booking/events/",
        json={
            "booking_id": booking_id,
            "event_type": "Created",
            "actor_type": "Customer",
            "actor_id": None,
            "payload": {"source": "test"},
        },
    )

    assert event_response.status_code == 201
    event_id = event_response.json()["id"]

    delete_version = await db_client.delete(f"/api/v1/crud/booking/versions/{version_id}")
    assert delete_version.status_code == 204

    delete_event = await db_client.delete(f"/api/v1/crud/booking/events/{event_id}")
    assert delete_event.status_code == 204
