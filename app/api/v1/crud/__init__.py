"""CRUD domain routers."""

from fastapi import APIRouter

from app.api.v1.crud.admin import router as admin_router
from app.api.v1.crud.auth import router as auth_router
from app.api.v1.crud.availability import router as availability_router
from app.api.v1.crud.booking import router as booking_router
from app.api.v1.crud.business import router as business_router
from app.api.v1.crud.customer import router as customer_router
from app.api.v1.crud.notification import router as notification_router
from app.api.v1.crud.payment import router as payment_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(admin_router)
router.include_router(business_router)
router.include_router(customer_router)
router.include_router(availability_router)
router.include_router(booking_router)
router.include_router(payment_router)
router.include_router(notification_router)
