"""CRUD routes for customer domain."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.agents.logging import logger
from app.api.deps import get_current_session_async
from app.api.v1.crud.base import CrudResource, build_resource_router
from app.models.customer import CustomerProfile, CustomerUser, UserIdentifier
from app.schemas.customer import (
    CustomerProfileCreate,
    CustomerProfileRead,
    CustomerProfileUpdate,
    CustomerUserCreate,
    CustomerUserRead,
    CustomerUserUpdate,
    UserIdentifierCreate,
    UserIdentifierRead,
    UserIdentifierUpdate,
)

router = APIRouter(prefix="/crud/customer", tags=["customer"], dependencies=[Depends(get_current_session_async)])


async def resolve_identifier_business(data: dict, db_session: AsyncSession) -> dict:
    customer_id = data.get("customer_id")
    if customer_id is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="customer_id is required")

    result = await db_session.exec(select(CustomerProfile).where(CustomerProfile.id == customer_id))
    customer = result.first()
    if customer is None:
        logger.info("user_identifier_customer_missing", customer_id=str(customer_id))
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")

    payload_business_id = data.get("business_id")
    if payload_business_id is not None and payload_business_id != customer.business_id:
        logger.info(
            "user_identifier_business_mismatch",
            customer_id=str(customer_id),
            payload_business_id=str(payload_business_id),
            customer_business_id=str(customer.business_id),
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="business_id does not match customer")

    data["business_id"] = customer.business_id
    return data


resources = [
    CrudResource(
        name="profiles",
        model=CustomerProfile,
        create_schema=CustomerProfileCreate,
        update_schema=CustomerProfileUpdate,
        read_schema=CustomerProfileRead,
        id_type=UUID,
    ),
    CrudResource(
        name="users",
        model=CustomerUser,
        create_schema=CustomerUserCreate,
        update_schema=CustomerUserUpdate,
        read_schema=CustomerUserRead,
        id_type=UUID,
    ),
    CrudResource(
        name="identifiers",
        model=UserIdentifier,
        create_schema=UserIdentifierCreate,
        update_schema=UserIdentifierUpdate,
        read_schema=UserIdentifierRead,
        id_type=UUID,
        create_transform=resolve_identifier_business,
    ),
]

for resource in resources:
    router.include_router(build_resource_router(resource))
