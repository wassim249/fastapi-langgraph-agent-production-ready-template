"""CRUD routes for payment domain."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_session_async
from app.api.v1.crud.base import CrudResource, build_resource_router
from app.models.payment import PaymentIntent, PaymentSetting, PaymentTransaction
from app.schemas.payment import (
    PaymentIntentCreate,
    PaymentIntentRead,
    PaymentIntentUpdate,
    PaymentSettingCreate,
    PaymentSettingRead,
    PaymentSettingUpdate,
    PaymentTransactionCreate,
    PaymentTransactionRead,
    PaymentTransactionUpdate,
)

router = APIRouter(prefix="/crud/payment", tags=["payment"], dependencies=[Depends(get_current_session_async)])

resources = [
    CrudResource(
        name="settings",
        model=PaymentSetting,
        create_schema=PaymentSettingCreate,
        update_schema=PaymentSettingUpdate,
        read_schema=PaymentSettingRead,
        id_type=UUID,
    ),
    CrudResource(
        name="intents",
        model=PaymentIntent,
        create_schema=PaymentIntentCreate,
        update_schema=PaymentIntentUpdate,
        read_schema=PaymentIntentRead,
        id_type=UUID,
    ),
    CrudResource(
        name="transactions",
        model=PaymentTransaction,
        create_schema=PaymentTransactionCreate,
        update_schema=PaymentTransactionUpdate,
        read_schema=PaymentTransactionRead,
        id_type=UUID,
    ),
]

for resource in resources:
    router.include_router(build_resource_router(resource))
