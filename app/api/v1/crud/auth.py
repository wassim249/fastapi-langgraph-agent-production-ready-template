"""CRUD routes for auth domain."""

from fastapi import APIRouter, Depends

from app.api.deps import get_current_session_async
from app.api.v1.crud.base import CrudResource, build_resource_router
from app.models.session import Session as AuthSession
from app.models.user import User as AuthUser
from app.schemas.auth_models import (
    AuthSessionCreate,
    AuthSessionRead,
    AuthSessionUpdate,
    AuthUserCreate,
    AuthUserRead,
    AuthUserUpdate,
)

router = APIRouter(prefix="/crud/auth", tags=["auth"], dependencies=[Depends(get_current_session_async)])

resources = [
    CrudResource(
        name="users",
        model=AuthUser,
        create_schema=AuthUserCreate,
        update_schema=AuthUserUpdate,
        read_schema=AuthUserRead,
        id_type=int,
    ),
    CrudResource(
        name="sessions",
        model=AuthSession,
        create_schema=AuthSessionCreate,
        update_schema=AuthSessionUpdate,
        read_schema=AuthSessionRead,
        id_type=str,
    ),
]

for resource in resources:
    router.include_router(build_resource_router(resource))
