"""CRUD routes for admin domain."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_session_async
from app.api.v1.crud.base import CrudResource, build_resource_router
from app.models.admin import AdminIdentifier, AdminProfile
from app.schemas.admin import (
    AdminIdentifierCreate,
    AdminIdentifierRead,
    AdminIdentifierUpdate,
    AdminProfileCreate,
    AdminProfileRead,
    AdminProfileUpdate,
)

router = APIRouter(prefix="/crud/admin", tags=["admin"], dependencies=[Depends(get_current_session_async)])

resources = [
    CrudResource(
        name="profiles",
        model=AdminProfile,
        create_schema=AdminProfileCreate,
        update_schema=AdminProfileUpdate,
        read_schema=AdminProfileRead,
        id_type=UUID,
    ),
    CrudResource(
        name="identifiers",
        model=AdminIdentifier,
        create_schema=AdminIdentifierCreate,
        update_schema=AdminIdentifierUpdate,
        read_schema=AdminIdentifierRead,
        id_type=UUID,
    ),
]

for resource in resources:
    router.include_router(build_resource_router(resource))
