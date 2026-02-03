"""CRUD tests for availability endpoints."""

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_weekly_rules_crud(db_client):
    payload = {
        "business_id": str(uuid4()),
        "branch_id": str(uuid4()),
        "name": "Weekdays",
        "days_of_week": [1, 2, 3, 4, 5],
        "start_time_local": "09:00:00",
        "end_time_local": "18:00:00",
        "slot_interval_minutes": 30,
        "active": True,
    }

    create_response = await db_client.post("/api/v1/crud/availability/weekly-rules/", json=payload)
    assert create_response.status_code == 201
    rule_id = create_response.json()["id"]

    get_response = await db_client.get(f"/api/v1/crud/availability/weekly-rules/{rule_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/availability/weekly-rules/{rule_id}",
        json={"slot_interval_minutes": 60},
    )
    assert update_response.status_code == 200
    assert update_response.json()["slot_interval_minutes"] == 60

    delete_response = await db_client.delete(f"/api/v1/crud/availability/weekly-rules/{rule_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_datetime_rules_crud(db_client):
    payload = {
        "business_id": str(uuid4()),
        "branch_id": str(uuid4()),
        "name": "Holiday",
        "rule_effect": "BLOCK",
        "start_at": "2026-02-15T00:00:00Z",
        "end_at": "2026-02-15T23:59:59Z",
        "priority": 100,
        "active": True,
    }

    create_response = await db_client.post("/api/v1/crud/availability/datetime-rules/", json=payload)
    assert create_response.status_code == 201
    rule_id = create_response.json()["id"]

    get_response = await db_client.get(f"/api/v1/crud/availability/datetime-rules/{rule_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/availability/datetime-rules/{rule_id}",
        json={"priority": 50},
    )
    assert update_response.status_code == 200
    assert update_response.json()["priority"] == 50

    delete_response = await db_client.delete(f"/api/v1/crud/availability/datetime-rules/{rule_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_slots_crud(db_client):
    payload = {
        "business_id": str(uuid4()),
        "branch_id": str(uuid4()),
        "start_at": "2026-02-15T10:00:00Z",
        "end_at": "2026-02-15T10:30:00Z",
        "capacity": 1,
        "status": "Open",
    }

    create_response = await db_client.post("/api/v1/crud/availability/slots/", json=payload)
    assert create_response.status_code == 201
    slot_id = create_response.json()["id"]

    get_response = await db_client.get(f"/api/v1/crud/availability/slots/{slot_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/availability/slots/{slot_id}",
        json={"capacity": 2},
    )
    assert update_response.status_code == 200
    assert update_response.json()["capacity"] == 2

    delete_response = await db_client.delete(f"/api/v1/crud/availability/slots/{slot_id}")
    assert delete_response.status_code == 204
