"""CRUD tests for customer endpoints."""

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_customer_profiles_crud(db_client):
    payload = {
        "business_id": str(uuid4()),
        "user_id": str(uuid4()),
        "display_name": "John Doe",
        "telno": "+66-81-234-5678",
        "line_user_id": "U1234567890abcdef",
        "notes": "VIP",
        "locale": "en-US",
        "timezone": "Asia/Bangkok",
    }

    create_response = await db_client.post("/api/v1/crud/customer/profiles/", json=payload)
    assert create_response.status_code == 201
    profile = create_response.json()
    profile_id = profile["id"]

    get_response = await db_client.get(f"/api/v1/crud/customer/profiles/{profile_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/customer/profiles/{profile_id}",
        json={"display_name": "Updated Name"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["display_name"] == "Updated Name"

    delete_response = await db_client.delete(f"/api/v1/crud/customer/profiles/{profile_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_customer_users_crud(db_client):
    payload = {"status": "active"}

    create_response = await db_client.post("/api/v1/crud/customer/users/", json=payload)
    assert create_response.status_code == 201
    user = create_response.json()
    user_id = user["id"]

    get_response = await db_client.get(f"/api/v1/crud/customer/users/{user_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/customer/users/{user_id}",
        json={"status": "blocked"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "blocked"

    delete_response = await db_client.delete(f"/api/v1/crud/customer/users/{user_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_customer_identifiers_crud(db_client):
    payload = {
        "customer_id": str(uuid4()),
        "type": "LINE",
        "identifier": "U1234567890abcdef",
        "is_verified": False,
        "status": "active",
        "metadata": {"source": "test"},
    }

    create_response = await db_client.post("/api/v1/crud/customer/identifiers/", json=payload)
    assert create_response.status_code == 201
    identifier = create_response.json()
    identifier_id = identifier["id"]

    get_response = await db_client.get(f"/api/v1/crud/customer/identifiers/{identifier_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/customer/identifiers/{identifier_id}",
        json={"is_verified": True},
    )
    assert update_response.status_code == 200
    assert update_response.json()["is_verified"] is True

    delete_response = await db_client.delete(f"/api/v1/crud/customer/identifiers/{identifier_id}")
    assert delete_response.status_code == 204
