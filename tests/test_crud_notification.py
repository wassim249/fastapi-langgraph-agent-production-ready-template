"""CRUD tests for notification endpoints."""

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_notification_jobs_crud(db_client):
    payload = {
        "business_id": str(uuid4()),
        "booking_id": str(uuid4()),
        "channel": "LINE",
        "template": "BookingCreated",
        "scheduled_at": "2026-02-15T09:00:00Z",
        "status": "Queued",
        "payload": {"test": True},
    }

    create_response = await db_client.post("/api/v1/crud/notification/jobs/", json=payload)
    assert create_response.status_code == 201
    job_id = create_response.json()["id"]

    get_response = await db_client.get(f"/api/v1/crud/notification/jobs/{job_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/notification/jobs/{job_id}",
        json={"status": "Sent"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Sent"

    delete_response = await db_client.delete(f"/api/v1/crud/notification/jobs/{job_id}")
    assert delete_response.status_code == 204
