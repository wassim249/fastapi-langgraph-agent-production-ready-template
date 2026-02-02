"""CRUD routes for customer domain."""

from uuid import UUID

from fastapi import APIRouter, Depends

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
    ),
]

for resource in resources:
    router.include_router(build_resource_router(resource))
