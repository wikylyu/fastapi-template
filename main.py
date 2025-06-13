import asyncio
import traceback
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from config import (
    ADMIN_USERNAME_PATTERN,
    APPNAME,
    APPVERSION,
    COPYRIGHT,
    CORS_ALLOW_ORIGIN,
    DATABASE_AUTO_UPGRADE,
    DEBUG,
)
from dal.admin import AdminRepo
from database.session import get_db
from middlewares.exception import ApiExceptionHandlingMiddleware
from routers import admin, auth, system
from schemas.base import ConfigSchema
from schemas.response import R


async def run_db_upgrade():
    from alembic import command
    from alembic.config import Config

    # 设置 Alembic 配置文件的路径
    alembic_cfg = Config("alembic.ini")

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, command.upgrade, alembic_cfg, "head")
    print("Database migration completed successfully")


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        if DATABASE_AUTO_UPGRADE:
            await run_db_upgrade()
    except Exception:
        traceback.print_exc()
    yield


app = FastAPI(title=APPNAME, version=APPVERSION, lifespan=lifespan, debug=DEBUG)

app.add_middleware(ApiExceptionHandlingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ALLOW_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
admin_router = APIRouter()
admin_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
admin_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
admin_router.include_router(system.router, prefix="/system", tags=["System"])


@admin_router.get("/config", response_model=R[ConfigSchema], summary="获取系统配置", description="获取系统配置")
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


app.include_router(admin_router, prefix="/adminapi")
