"""Shared CRUD router utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.agents.config import settings
from app.agents.limiter import limiter
from app.agents.logging import logger
from app.models.common import utc_now
from app.services.db_session import get_async_session


@dataclass(frozen=True)
class CrudResource:
    name: str
    model: Type[SQLModel]
    create_schema: Type[SQLModel]
    update_schema: Type[SQLModel]
    read_schema: Type[SQLModel]
    id_type: Type
    create_transform: Optional[Callable[[Dict[str, Any], AsyncSession], Awaitable[Dict[str, Any]]]] = None


def build_resource_router(resource: CrudResource) -> APIRouter:
    """Build a CRUD router for a single resource."""
    router = APIRouter(prefix=f"/{resource.name}", tags=[resource.name])

    def parse_id(raw_id: str):
        try:
            return resource.id_type(raw_id)
        except (TypeError, ValueError) as exc:
            logger.error("crud_invalid_id", resource=resource.name, raw_id=raw_id, error=str(exc))
            raise HTTPException(status_code=422, detail="Invalid id format")

    @router.post("/", response_model=resource.read_schema, status_code=status.HTTP_201_CREATED)
    @limiter.limit(settings.RATE_LIMIT_ENDPOINTS["crud_write"][0])
    async def create_item(
        request: Request,
        payload: dict,
        db_session: AsyncSession = Depends(get_async_session),
    ):
        try:
            validated = resource.create_schema.model_validate(payload)
            data = validated.model_dump()
            if resource.create_transform is not None:
                data = await resource.create_transform(data, db_session)
            record = resource.model(**data)
            db_session.add(record)
            await db_session.commit()
            await db_session.refresh(record)
            logger.info("crud_created", resource=resource.name, record_id=str(record.id))
            return record
        except SQLAlchemyError as exc:
            logger.exception("crud_create_failed", resource=resource.name, error=str(exc))
            raise HTTPException(status_code=500, detail="Failed to create record")

    @router.get("/", response_model=List[resource.read_schema])
    @limiter.limit(settings.RATE_LIMIT_ENDPOINTS["crud_read"][0])
    async def list_items(
        request: Request,
        limit: int = 100,
        offset: int = 0,
        db_session: AsyncSession = Depends(get_async_session),
    ):
        result = await db_session.exec(select(resource.model).offset(offset).limit(limit))
        return result.all()

    @router.get("/{item_id}", response_model=resource.read_schema)
    @limiter.limit(settings.RATE_LIMIT_ENDPOINTS["crud_read"][0])
    async def get_item(
        request: Request,
        item_id: str,
        db_session: AsyncSession = Depends(get_async_session),
    ):
        parsed_id = parse_id(item_id)
        result = await db_session.exec(select(resource.model).where(resource.model.id == parsed_id))
        record = result.first()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return record

    @router.patch("/{item_id}", response_model=resource.read_schema)
    @limiter.limit(settings.RATE_LIMIT_ENDPOINTS["crud_write"][0])
    async def update_item(
        request: Request,
        item_id: str,
        payload: dict,
        db_session: AsyncSession = Depends(get_async_session),
    ):
        parsed_id = parse_id(item_id)
        result = await db_session.exec(select(resource.model).where(resource.model.id == parsed_id))
        record = result.first()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")

        validated = resource.update_schema.model_validate(payload)
        data = validated.model_dump(exclude_unset=True)
        for key, value in data.items():
            setattr(record, key, value)

        if hasattr(record, "updated_at"):
            setattr(record, "updated_at", utc_now())

        try:
            db_session.add(record)
            await db_session.commit()
            await db_session.refresh(record)
            logger.info("crud_updated", resource=resource.name, record_id=str(record.id))
            return record
        except SQLAlchemyError as exc:
            logger.exception("crud_update_failed", resource=resource.name, error=str(exc))
            raise HTTPException(status_code=500, detail="Failed to update record")

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    @limiter.limit(settings.RATE_LIMIT_ENDPOINTS["crud_write"][0])
    async def delete_item(
        request: Request,
        item_id: str,
        db_session: AsyncSession = Depends(get_async_session),
    ):
        parsed_id = parse_id(item_id)
        result = await db_session.exec(select(resource.model).where(resource.model.id == parsed_id))
        record = result.first()
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")

        try:
            db_session.delete(record)
            await db_session.commit()
            logger.info("crud_deleted", resource=resource.name, record_id=str(parsed_id))
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except SQLAlchemyError as exc:
            logger.exception("crud_delete_failed", resource=resource.name, error=str(exc))
            raise HTTPException(status_code=500, detail="Failed to delete record")

    return router
