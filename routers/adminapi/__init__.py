from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_USERNAME_PATTERN, APPNAME, APPVERSION, COPYRIGHT
from dal.admin import AdminRepo
from database.session import get_db
from routers.adminapi.schemas.admin import ConfigSchema
from routers.response import R

from . import admin, auth, system

router = APIRouter()
router.include_router(auth.router, prefix="/auth", tags=["Admin Auth"])
router.include_router(admin.router, prefix="/admin", tags=["Admin User"])
router.include_router(system.router, prefix="/system", tags=["System"])


@router.get("/config", response_model=R[ConfigSchema], summary="获取系统配置", description="获取系统配置")
async def get_config(db: AsyncSession = Depends(get_db)):
    cfg = {
        "appname": APPNAME,
        "copyright": COPYRIGHT,
        "version": APPVERSION,
        "admin_username_pattern": ADMIN_USERNAME_PATTERN,
    }
    cfg["onboarding"] = not await AdminRepo.check_super_admin_user_exists(
        db
    )  # onboarding表示是否存在超级管理员，不存在则可以创建
    return R.success(cfg)
