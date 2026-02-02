"""CRUD routes for booking domain."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_session_async
from app.api.v1.crud.base import CrudResource, build_resource_router
from app.models.booking import Booking, BookingEvent, BookingVersion
from app.schemas.booking import (
    BookingCreate,
    BookingEventCreate,
    BookingEventRead,
    BookingEventUpdate,
    BookingRead,
    BookingUpdate,
    BookingVersionCreate,
    BookingVersionRead,
    BookingVersionUpdate,
)

router = APIRouter(prefix="/crud/booking", tags=["booking"], dependencies=[Depends(get_current_session_async)])

resources = [
    CrudResource(
        name="bookings",
        model=Booking,
        create_schema=BookingCreate,
        update_schema=BookingUpdate,
        read_schema=BookingRead,
        id_type=UUID,
    ),
    CrudResource(
        name="versions",
        model=BookingVersion,
        create_schema=BookingVersionCreate,
        update_schema=BookingVersionUpdate,
        read_schema=BookingVersionRead,
        id_type=UUID,
    ),
    CrudResource(
        name="events",
        model=BookingEvent,
        create_schema=BookingEventCreate,
        update_schema=BookingEventUpdate,
        read_schema=BookingEventRead,
        id_type=UUID,
    ),
]

for resource in resources:
    router.include_router(build_resource_router(resource))
