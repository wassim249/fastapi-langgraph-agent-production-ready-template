"""CRUD tests for auth domain endpoints."""

import pytest


@pytest.mark.asyncio
async def test_auth_users_crud(db_client):
    payload = {
        "email": "user@example.com",
        "hashed_password": "hashed_password_here",
    }

    create_response = await db_client.post("/api/v1/crud/auth/users/", json=payload)
    assert create_response.status_code == 201
    user = create_response.json()
    user_id = user["id"]

    get_response = await db_client.get(f"/api/v1/crud/auth/users/{user_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/auth/users/{user_id}",
        json={"email": "updated@example.com"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["email"] == "updated@example.com"

    delete_response = await db_client.delete(f"/api/v1/crud/auth/users/{user_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_auth_sessions_crud(db_client):
    payload = {
        "id": "session-123",
        "user_id": 1,
        "name": "My Session",
    }

    create_response = await db_client.post("/api/v1/crud/auth/sessions/", json=payload)
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    get_response = await db_client.get(f"/api/v1/crud/auth/sessions/{session_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/auth/sessions/{session_id}",
        json={"name": "Updated Session"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Session"

    delete_response = await db_client.delete(f"/api/v1/crud/auth/sessions/{session_id}")
    assert delete_response.status_code == 204
