"""CRUD tests for business endpoints."""

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_business_crud(db_client):
    payload = {
        "name": "My Business",
        "business_type": "Salon",
        "timezone": "Asia/Bangkok",
        "location": "123 Main St",
        "logo_url": "https://example.com/logo.png",
        "status": "active",
    }

    create_response = await db_client.post("/api/v1/crud/business/businesses/", json=payload)
    assert create_response.status_code == 201
    created = create_response.json()
    business_id = created["id"]

    list_response = await db_client.get("/api/v1/crud/business/businesses/?limit=10&offset=0")
    assert list_response.status_code == 200
    assert any(item["id"] == business_id for item in list_response.json())

    get_response = await db_client.get(f"/api/v1/crud/business/businesses/{business_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == business_id

    update_response = await db_client.patch(
        f"/api/v1/crud/business/businesses/{business_id}",
        json={"name": "Updated Business"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Business"

    delete_response = await db_client.delete(f"/api/v1/crud/business/businesses/{business_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_branch_and_service_crud(db_client):
    business_response = await db_client.post(
        "/api/v1/crud/business/businesses/",
        json={
            "name": "Branch Business",
            "business_type": "Spa",
            "timezone": "Asia/Bangkok",
            "status": "active",
        },
    )
    business_id = business_response.json()["id"]

    branch_response = await db_client.post(
        "/api/v1/crud/business/branches/",
        json={
            "business_id": business_id,
            "name": "Main Branch",
            "location": "456 Main St",
            "tel_no": "+66-2-123-4567",
            "status": "open",
        },
    )

    assert branch_response.status_code == 201
    branch_id = branch_response.json()["id"]

    service_response = await db_client.post(
        "/api/v1/crud/business/services/",
        json={
            "branch_id": branch_id,
            "business_id": business_id,
            "name": "Haircut",
            "duration_minutes": 30,
            "price_amount": "500.00",
            "price_currency": "THB",
            "deposit_required": False,
            "deposit_amount": None,
            "active": True,
        },
    )

    assert service_response.status_code == 201
    service_id = service_response.json()["id"]

    update_service = await db_client.patch(
        f"/api/v1/crud/business/services/{service_id}",
        json={"name": "Premium Haircut"},
    )

    assert update_service.status_code == 200
    assert update_service.json()["name"] == "Premium Haircut"

    delete_service = await db_client.delete(f"/api/v1/crud/business/services/{service_id}")
    assert delete_service.status_code == 204


@pytest.mark.asyncio
async def test_memberships_crud(db_client):
    payload = {
        "business_id": str(uuid4()),
        "admin_user_id": str(uuid4()),
        "role": "Owner",
        "status": "active",
    }

    create_response = await db_client.post("/api/v1/crud/business/memberships/", json=payload)
    assert create_response.status_code == 201
    membership_id = create_response.json()["id"]

    get_response = await db_client.get(f"/api/v1/crud/business/memberships/{membership_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/business/memberships/{membership_id}",
        json={"role": "Admin"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["role"] == "Admin"

    delete_response = await db_client.delete(f"/api/v1/crud/business/memberships/{membership_id}")
    assert delete_response.status_code == 204
