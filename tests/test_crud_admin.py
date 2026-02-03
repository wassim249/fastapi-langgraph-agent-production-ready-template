"""CRUD tests for admin endpoints."""

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_admin_profiles_crud(db_client):
    payload = {
        "email": "admin@example.com",
        "telno": "+66-81-234-5678",
        "name": "Admin User",
        "status": "active",
    }

    create_response = await db_client.post("/api/v1/crud/admin/profiles/", json=payload)
    assert create_response.status_code == 201
    admin_profile = create_response.json()
    admin_id = admin_profile["id"]

    list_response = await db_client.get("/api/v1/crud/admin/profiles/?limit=10&offset=0")
    assert list_response.status_code == 200
    assert any(item["id"] == admin_id for item in list_response.json())

    get_response = await db_client.get(f"/api/v1/crud/admin/profiles/{admin_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/admin/profiles/{admin_id}",
        json={"name": "Updated Admin"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Admin"

    delete_response = await db_client.delete(f"/api/v1/crud/admin/profiles/{admin_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_admin_identifiers_crud(db_client):
    admin_id = str(uuid4())
    payload = {
        "admin_id": admin_id,
        "type": "LINE",
        "identifier": "U1234567890abcdef",
        "is_verified": False,
        "status": "active",
        "metadata": {"source": "test"},
    }

    create_response = await db_client.post("/api/v1/crud/admin/identifiers/", json=payload)
    assert create_response.status_code == 201
    identifier = create_response.json()
    identifier_id = identifier["id"]

    get_response = await db_client.get(f"/api/v1/crud/admin/identifiers/{identifier_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/admin/identifiers/{identifier_id}",
        json={"is_verified": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_verified"] is True

    delete_response = await db_client.delete(f"/api/v1/crud/admin/identifiers/{identifier_id}")
    assert delete_response.status_code == 204
