"""Health and root endpoint tests."""

import pytest

from app import main


@pytest.mark.asyncio
async def test_root(client):
    response = await client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data


@pytest.mark.asyncio
async def test_health(client, monkeypatch):
    async def healthy_check() -> bool:
        return True

    monkeypatch.setattr(main.database_service, "health_check", healthy_check)

    response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert data["components"]["database"] == "healthy"
    assert "timestamp" in data


@pytest.mark.asyncio
async def test_api_health(client):
    response = await client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"
    assert "version" in data
