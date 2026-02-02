"""CRUD routes for availability domain."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_session_async
from app.api.v1.crud.base import CrudResource, build_resource_router
from app.models.availability import AvailabilitySlot, DatetimeAvailabilityRule, WeeklyAvailabilityRule
from app.schemas.availability import (
    AvailabilitySlotCreate,
    AvailabilitySlotRead,
    AvailabilitySlotUpdate,
    DatetimeAvailabilityRuleCreate,
    DatetimeAvailabilityRuleRead,
    DatetimeAvailabilityRuleUpdate,
    WeeklyAvailabilityRuleCreate,
    WeeklyAvailabilityRuleRead,
    WeeklyAvailabilityRuleUpdate,
)

router = APIRouter(prefix="/crud/availability", tags=["availability"], dependencies=[Depends(get_current_session_async)])

resources = [
    CrudResource(
        name="weekly-rules",
        model=WeeklyAvailabilityRule,
        create_schema=WeeklyAvailabilityRuleCreate,
        update_schema=WeeklyAvailabilityRuleUpdate,
        read_schema=WeeklyAvailabilityRuleRead,
        id_type=UUID,
    ),
    CrudResource(
        name="datetime-rules",
        model=DatetimeAvailabilityRule,
        create_schema=DatetimeAvailabilityRuleCreate,
        update_schema=DatetimeAvailabilityRuleUpdate,
        read_schema=DatetimeAvailabilityRuleRead,
        id_type=UUID,
    ),
    CrudResource(
        name="slots",
        model=AvailabilitySlot,
        create_schema=AvailabilitySlotCreate,
        update_schema=AvailabilitySlotUpdate,
        read_schema=AvailabilitySlotRead,
        id_type=UUID,
    ),
]

for resource in resources:
    router.include_router(build_resource_router(resource))
