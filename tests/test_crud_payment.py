"""CRUD tests for payment endpoints."""

from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_payment_settings_crud(db_client):
    payload = {
        "business_id": str(uuid4()),
        "provider": "PromptPay",
        "status": "active",
        "config": {"mode": "test"},
    }

    create_response = await db_client.post("/api/v1/crud/payment/settings/", json=payload)
    assert create_response.status_code == 201
    setting = create_response.json()
    setting_id = setting["id"]

    get_response = await db_client.get(f"/api/v1/crud/payment/settings/{setting_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == setting_id

    update_response = await db_client.patch(
        f"/api/v1/crud/payment/settings/{setting_id}",
        json={"status": "inactive"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "inactive"

    delete_response = await db_client.delete(f"/api/v1/crud/payment/settings/{setting_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_payment_intents_crud(db_client):
    payload = {
        "business_id": str(uuid4()),
        "booking_id": str(uuid4()),
        "provider": "PromptPay",
        "amount": "500.00",
        "currency": "THB",
        "status": "Created",
    }

    create_response = await db_client.post("/api/v1/crud/payment/intents/", json=payload)
    assert create_response.status_code == 201
    intent_id = create_response.json()["id"]

    get_response = await db_client.get(f"/api/v1/crud/payment/intents/{intent_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/payment/intents/{intent_id}",
        json={"status": "Succeeded"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Succeeded"

    delete_response = await db_client.delete(f"/api/v1/crud/payment/intents/{intent_id}")
    assert delete_response.status_code == 204


@pytest.mark.asyncio
async def test_payment_transactions_crud(db_client):
    payload = {
        "payment_intent_id": str(uuid4()),
        "status": "Succeeded",
        "provider_payload": {"provider": "test"},
    }

    create_response = await db_client.post("/api/v1/crud/payment/transactions/", json=payload)
    assert create_response.status_code == 201
    transaction_id = create_response.json()["id"]

    get_response = await db_client.get(f"/api/v1/crud/payment/transactions/{transaction_id}")
    assert get_response.status_code == 200

    update_response = await db_client.patch(
        f"/api/v1/crud/payment/transactions/{transaction_id}",
        json={"status": "Refunded"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "Refunded"

    delete_response = await db_client.delete(f"/api/v1/crud/payment/transactions/{transaction_id}")
    assert delete_response.status_code == 204
