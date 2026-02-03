"""Chatbot endpoint tests."""

from uuid import uuid4

import pytest


@pytest.fixture
async def session_headers(db_client):
    email = f"user-{uuid4().hex}@example.com"
    password = "SecurePass123!"

    register_response = await db_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    assert register_response.status_code == 200

    login_response = await db_client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password, "grant_type": "password"},
    )
    assert login_response.status_code == 200
    user_token = login_response.json()["access_token"]

    session_response = await db_client.post(
        "/api/v1/auth/session",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert session_response.status_code == 200
    session_token = session_response.json()["token"]["access_token"]
    return {"Authorization": f"Bearer {session_token}"}


@pytest.mark.asyncio
async def test_chat(db_client, session_headers):
    response = await db_client.post(
        "/api/v1/chatbot/chat",
        json={"messages": [{"role": "user", "content": "Hello"}]},
        headers=session_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["messages"][-1]["role"] == "assistant"


@pytest.mark.asyncio
async def test_chat_stream(db_client, session_headers):
    response = await db_client.post(
        "/api/v1/chatbot/chat/stream",
        json={"messages": [{"role": "user", "content": "Hello"}]},
        headers=session_headers,
    )

    assert response.status_code == 200
    assert "data:" in response.text


@pytest.mark.asyncio
async def test_messages(db_client, session_headers):
    response = await db_client.get(
        "/api/v1/chatbot/messages",
        headers=session_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["messages"]


@pytest.mark.asyncio
async def test_clear_messages(db_client, session_headers):
    response = await db_client.delete(
        "/api/v1/chatbot/messages",
        headers=session_headers,
    )

    assert response.status_code == 200
    assert "message" in response.json()
