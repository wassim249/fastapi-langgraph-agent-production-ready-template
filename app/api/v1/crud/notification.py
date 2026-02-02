"""CRUD routes for notification domain."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_current_session_async
from app.api.v1.crud.base import CrudResource, build_resource_router
from app.models.notification import NotificationJob
from app.schemas.notification import (
    NotificationJobCreate,
    NotificationJobRead,
    NotificationJobUpdate,
)

router = APIRouter(prefix="/crud/notification", tags=["notification"], dependencies=[Depends(get_current_session_async)])

resources = [
    CrudResource(
        name="jobs",
        model=NotificationJob,
        create_schema=NotificationJobCreate,
        update_schema=NotificationJobUpdate,
        read_schema=NotificationJobRead,
        id_type=UUID,
    ),
]

for resource in resources:
    router.include_router(build_resource_router(resource))
