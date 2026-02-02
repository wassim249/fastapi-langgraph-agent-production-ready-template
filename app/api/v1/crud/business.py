"""CRUD routes for business domain."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_session_async
from app.api.v1.crud.base import CrudResource, build_resource_router
from app.models.business import Branch, Business, BusinessMembership, Service
from app.schemas.business import (
    BranchCreate,
    BranchRead,
    BranchUpdate,
    BusinessCreate,
    BusinessMembershipCreate,
    BusinessMembershipRead,
    BusinessMembershipUpdate,
    BusinessRead,
    BusinessUpdate,
    ServiceCreate,
    ServiceRead,
    ServiceUpdate,
)

router = APIRouter(prefix="/crud/business", tags=["business"], dependencies=[Depends(get_current_session_async)])

resources = [
    CrudResource(
        name="businesses",
        model=Business,
        create_schema=BusinessCreate,
        update_schema=BusinessUpdate,
        read_schema=BusinessRead,
        id_type=UUID,
    ),
    CrudResource(
        name="branches",
        model=Branch,
        create_schema=BranchCreate,
        update_schema=BranchUpdate,
        read_schema=BranchRead,
        id_type=UUID,
    ),
    CrudResource(
        name="services",
        model=Service,
        create_schema=ServiceCreate,
        update_schema=ServiceUpdate,
        read_schema=ServiceRead,
        id_type=UUID,
    ),
    CrudResource(
        name="memberships",
        model=BusinessMembership,
        create_schema=BusinessMembershipCreate,
        update_schema=BusinessMembershipUpdate,
        read_schema=BusinessMembershipRead,
        id_type=UUID,
    ),
]

for resource in resources:
    router.include_router(build_resource_router(resource))
