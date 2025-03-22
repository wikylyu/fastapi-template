from datetime import datetime, timedelta, timezone

from captcha.image import ImageCaptcha
from fastapi import APIRouter, Depends, Header, Request, Response
from pydantic import BaseModel, Field
from redis import asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_USERNAME_PATTERN, APPNAME, APPVERSION, COPYRIGHT
from dal.admin import AdminRepo
from database.redis import get_redis
from database.session import get_db
from middlewares.depends import get_admin_user, get_admin_user_token, get_real_ip
from models.admin import AdminUserStatus, AdminUserToken, AdminUserTokenStatus
from routers.api import ApiErrors, ApiException
from schemas.admin import AdminConfigSchema, AdminUserSchema, AdminUserTokenSchema
from schemas.response import R
from services.encrypt import encrypt_service
from utils.string import random_str
from utils.uuid import uuidv4

router = APIRouter()


@router.get("/config", response_model=R[AdminConfigSchema], summary="获取管理配置", description="获取系统配置")
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
async def create_superuser(req_form: CreateSuperuserForm, db: AsyncSession = Depends(get_db)):
    if await AdminRepo.check_super_admin_user_exists(db):
        raise ApiException(ApiErrors.ADMIN_SUPERUSER_EXISTS)
    admin_user = await AdminRepo.create_admin_user(
        db, req_form.username, req_form.name, req_form.password, is_superuser=True
    )
    return R.success(admin_user)


@router.get("/login/captcha", summary="获取登录验证码", description="获取登录验证码的图片内容")
async def get_login_captcha(redis: aioredis.Redis = Depends(get_redis)):
    text = random_str(5)
    image = ImageCaptcha(width=300, height=100)
    img_data = image.generate(text)
    id = uuidv4()

    async with redis.client() as conn:
        await conn.set(f"login_captcha.{id}", text, ex=5 * 60)

    response = Response(
        content=img_data.read(),
        media_type="image/png",
    )
    response.set_cookie("login_captcha_id", id, expires=5 * 60)

    return response


class LoginForm(BaseModel):
    username: str = Field(max_length=32, min_length=1, pattern=ADMIN_USERNAME_PATTERN, description="用户名")
    password: str = Field(min_length=1, max_length=64, description="密码")
    captcha: str = Field(min_length=1, description="验证码")
    captcha_id: str = Field(default="")
    remember: bool = Field(default=False, description="如果记住，则维持登录7天，否则只有一天")


@router.put(
    "/login",
    response_model=R[AdminUserTokenSchema],
    summary="管理员登录",
    description="管理员登录，使用用户名和密码",
)
async def login(
    req_form: LoginForm,
    request: Request,
    response: Response,
    user_agent: str = Header(),
    ip: str = Depends(get_real_ip),
    db: AsyncSession = Depends(get_db),
    redis: aioredis.Redis = Depends(get_redis),
):
    admin_user = await AdminRepo.get_admin_user_by_username(db, req_form.username)
    if not admin_user:
        raise ApiException(ApiErrors.ADMIN_USER_NOT_FOUND)
    if admin_user.status != AdminUserStatus.ACTIVE.value:
        raise ApiException(ApiErrors.ADMIN_USER_BANNED)
    if not admin_user.auth(req_form.password):
        raise ApiException(ApiErrors.ADMIN_USER_PASSWORD_INCORRECT)
    captcha_id = req_form.captcha_id or request.cookies.get("login_captcha_id")
    if not captcha_id:
        raise ApiException(ApiErrors.ADMIN_CAPTCHA_INCORRECT)
    async with redis.client() as conn:
        captcha = await conn.getdel(f"login_captcha.{captcha_id}")
        if not captcha or captcha.lower() != req_form.captcha.lower():
            raise ApiException(ApiErrors.ADMIN_CAPTCHA_INCORRECT)

    expired_at = datetime.now() + timedelta(days=7 if req_form.remember else 1)
    admin_user_token = await AdminRepo.create_admin_user_token(
        db, admin_user.id, expired_at=expired_at, ip=ip, user_agent=user_agent
    )

    r = AdminUserTokenSchema.model_validate(admin_user_token)
    r.id = encrypt_service.encrypt(admin_user_token.id)

    response.set_cookie("admin_user_token", r.id, expires=expired_at.astimezone(timezone.utc))

    return R.success(r)


@router.get(
    "/profile",
    response_model=R[AdminUserSchema],
    summary="获取管理员信息",
    description="获取当前登录的管理员信息",
)
async def get_profile(admin_user: AdminUserSchema = Depends(get_admin_user)):
    return R.success(admin_user)


class UpdateProfileForm(BaseModel):
    name: str = Field(max_length=64, min_length=1)
    email: str = Field(max_length=64)
    phone: str = Field(max_length=32)


@router.put(
    "/profile", response_model=R[AdminUserSchema], summary="更新管理员信息", description="更新当前登录的管理员信息"
)
async def update_profile(
    req_form: UpdateProfileForm,
    admin_user: AdminUserSchema = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    admin_user.email = req_form.email
    admin_user.phone = req_form.phone
    admin_user.name = req_form.name
    return R.success(admin_user)


@router.put("/logout", response_model=R[None], summary="管理员登出", description="管理员登出，清除登录状态")
async def logout(response: Response, admin_user_token: AdminUserToken | None = Depends(get_admin_user_token)):
    response.delete_cookie("admin_user_token")
    if admin_user_token:
        admin_user_token.status = AdminUserTokenStatus.REVOKED.value
    return R.success(None)
