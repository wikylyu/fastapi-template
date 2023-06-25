from fastapi import APIRouter
from adminpi.staff import router as staff_router
from adminpi.admin import router as admin_router
from adminpi.user import router as user_router

adminpi_router = APIRouter(tags=['adminpi'])

adminpi_router.include_router(staff_router, prefix='/staff')
adminpi_router.include_router(admin_router, prefix='/admin')
adminpi_router.include_router(user_router, prefix='/user')
