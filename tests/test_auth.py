"""Authentication and session API tests."""

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_auth_flow(db_client):
    email = f"user-{uuid4().hex}@example.com"
    password = "SecurePass123!"

    register_response = await db_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )

    assert register_response.status_code == 200
    register_data = register_response.json()
    assert register_data["email"] == email
    assert register_data["token"]

    login_response = await db_client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password, "grant_type": "password"},
    )

    assert login_response.status_code == 200
    login_data = login_response.json()
    user_token = login_data["access_token"]

    session_response = await db_client.post(
        "/api/v1/auth/session",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert session_response.status_code == 200
    session_data = session_response.json()
    session_id = session_data["session_id"]
    session_token = session_data["token"]["access_token"]

    sessions_response = await db_client.get(
        "/api/v1/auth/sessions",
        headers={"Authorization": f"Bearer {user_token}"},
    )

    assert sessions_response.status_code == 200
    assert any(session["session_id"] == session_id for session in sessions_response.json())

    update_response = await db_client.patch(
        f"/api/v1/auth/session/{session_id}/name",
        data={"name": "My Session"},
        headers={"Authorization": f"Bearer {session_token}"},
    )

    assert update_response.status_code == 200
    assert update_response.json()["name"] == "My Session"

    delete_response = await db_client.delete(
        f"/api/v1/auth/session/{session_id}",
        headers={"Authorization": f"Bearer {session_token}"},
    )

    assert delete_response.status_code in {200, 204}
