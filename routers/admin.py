from fastapi import APIRouter
from pydantic import BaseModel, Field

from config import ADMIN_USERNAME_PATTERN, APPNAME, APPVERSION
from dal.admin import AdminRepo
from database.session import get_db
from models.admin import AdminUserStatus
from routers.api import ApiErrors, ApiException
from schemas.admin import AdminConfigSchema, AdminUserSchema
from schemas.response import R

router = APIRouter()


@router.get("/config", response_model=R[AdminConfigSchema], summary="获取管理配置", description="获取系统配置")
async def get_config():
    with get_db() as db:
        cfg = {
            "name": APPNAME,
            "version": APPVERSION,
            "admin_username_pattern": ADMIN_USERNAME_PATTERN,
        }
        cfg["onboarding"] = not AdminRepo.check_super_admin_user_exists(
            db
        )  # onboarding表示是否存在超级管理员，不存在则可以创建
        return R.success(cfg)


class CreateSuperuserForm(BaseModel):
    username: str = Field(min_length=4, max_length=32, pattern=ADMIN_USERNAME_PATTERN)
    name: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=6, max_length=64)


@router.post(
    "/superuser",
    response_model=R[AdminUserSchema],
    summary="创建超级管理员",
    description="创建超级管理员，只有在不存在超级管理员的时候可以创建",
)
async def create_superuser(req_form: CreateSuperuserForm):
    with get_db() as db:
        if AdminRepo.check_super_admin_user_exists(db):
            raise ApiException(ApiErrors.ADMIN_SUPERUSER_EXISTS)
        admin_user = AdminRepo.create_admin_user(
            db, req_form.username, req_form.name, req_form.password, is_superuser=True
        )
        return R.success(admin_user)


class LoginForm(BaseModel):
    username: str = Field(max_length=32, min_length=1, pattern=ADMIN_USERNAME_PATTERN)
    password: str = Field(min_length=1)


@router.put(
    "/login",
    response_model=R[AdminUserSchema],
    summary="管理员登录",
    description="管理员登录，使用用户名和密码",
)
async def login(req_form: LoginForm):
    with get_db() as db:
        admin_user = AdminRepo.get_admin_user_by_username(db, req_form.username)
        if not admin_user:
            raise ApiException(ApiErrors.ADMIN_USER_NOT_FOUND)
        if admin_user.status != AdminUserStatus.ACTIVE.value:
            raise ApiException(ApiErrors.ADMIN_USER_BANNED)
        if not admin_user.auth(req_form.password):
            raise ApiException(ApiErrors.ADMIN_USER_PASSWORD_INCORRECT)
        return R.success(admin_user)
