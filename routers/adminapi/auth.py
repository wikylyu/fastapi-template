import random
from datetime import datetime, timedelta, timezone

from captcha.image import ImageCaptcha
from fastapi import APIRouter, Depends, Header, Query, Request, Response
from pydantic import BaseModel, Field
from redis import asyncio as aioredis

from config import ADMIN_USERNAME_PATTERN
from dal.admin import AdminRepo
from dal.system import SystemRepo
from database.redis import get_redis
from middlewares.depends import get_client_real_ip, get_current_admin_user, try_current_admin_user_token
from models.admin import AdminUser, AdminUserStatus, AdminUserToken, AdminUserTokenStatus
from routers.adminapi.schemas.admin import AdminUserSchema, AdminUserTokenSchema
from routers.api import ApiErrors, ApiException
from routers.response import R
from services.encrypt import EncryptService, get_encrypt_service
from utils.string import random_str
from utils.uuid import uuidv4

router = APIRouter()


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
async def create_superuser(
    req_form: CreateSuperuserForm,
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    if await admin_repo.check_super_admin_user_exists():
        raise ApiException(ApiErrors.ADMIN_SUPERUSER_EXISTS)
    admin_user = await admin_repo.create_admin_user(
        req_form.username, req_form.name, req_form.password, is_superuser=True
    )
    return R.success(admin_user)


async def generate_captcha(redis: aioredis.Redis, name: str, ex: int = 5 * 60):
    text = random_str(random.choice([5, 6]))
    image = ImageCaptcha(width=300, height=100)
    img_data = image.generate(text)
    id = uuidv4()

    async with redis.client() as conn:
        await conn.set(f"{name}.{id}", text, ex=ex)

    response = Response(
        content=img_data.read(),
        media_type="image/png",
    )
    response.set_cookie(f"{name}_id", id, expires=ex)

    return response


@router.get(
    "/login/captcha",
    responses={200: {"content": {"image/png": {}}, "description": "返回一张 PNG 格式的图片,大小是300x100"}},
    summary="获取登录验证码",
    description="获取登录验证码的图片内容",
)
async def get_login_captcha(redis: aioredis.Redis = Depends(get_redis)):
    return await generate_captcha(redis, "login_captcha")


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
    ip: str = Depends(get_client_real_ip),
    redis: aioredis.Redis = Depends(get_redis),
    encrypt_service: EncryptService = Depends(get_encrypt_service),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    captcha_id = req_form.captcha_id or request.cookies.get("login_captcha_id")
    if not captcha_id:
        raise ApiException(ApiErrors.ADMIN_CAPTCHA_INCORRECT)
    async with redis.client() as conn:
        captcha = await conn.getdel(f"login_captcha.{captcha_id}")
        if not captcha or captcha.lower() != req_form.captcha.lower():
            raise ApiException(ApiErrors.ADMIN_CAPTCHA_INCORRECT)

    admin_user = await admin_repo.get_admin_user_by_username(req_form.username)
    if not admin_user:
        raise ApiException(ApiErrors.ADMIN_USER_NOT_FOUND)
    if admin_user.status != AdminUserStatus.ACTIVE.value:
        raise ApiException(ApiErrors.ADMIN_USER_BANNED)
    if not admin_user.auth(req_form.password):
        raise ApiException(ApiErrors.ADMIN_USER_PASSWORD_INCORRECT)

    expired_at = datetime.now() + timedelta(days=7 if req_form.remember else 1)
    admin_user_token = await admin_repo.create_admin_user_token(
        admin_user.id, expired_at=expired_at, ip=ip, user_agent=user_agent
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
async def get_profile(cuser: AdminUser = Depends(get_current_admin_user)):
    return R.success(cuser)


class UpdateProfileForm(BaseModel):
    name: str = Field(max_length=64, min_length=1)
    email: str = Field(max_length=64)
    phone: str = Field(max_length=32)


@router.put(
    "/profile", response_model=R[AdminUserSchema], summary="更新管理员信息", description="更新当前登录的管理员信息"
)
async def update_profile(
    req_form: UpdateProfileForm,
    cuser: AdminUser = Depends(get_current_admin_user),
):
    cuser.email = req_form.email
    cuser.phone = req_form.phone
    cuser.name = req_form.name
    return R.success(cuser)


@router.put("/logout", response_model=R[None], summary="管理员登出", description="管理员登出，清除登录状态")
async def logout(response: Response, admin_user_token: AdminUserToken | None = Depends(try_current_admin_user_token)):
    response.delete_cookie("admin_user_token")
    if admin_user_token:
        admin_user_token.status = AdminUserTokenStatus.REVOKED.value
    return R.success(None)


@router.get(
    "/password/captcha",
    responses={200: {"content": {"image/png": {}}, "description": "返回一张 PNG 格式的图片,大小是300x100"}},
    summary="获取修改密码验证码",
    description="获取修改密码验证码的图片内容",
)
async def get_password_captcha(redis: aioredis.Redis = Depends(get_redis)):
    return await generate_captcha(redis, "update_password_captcha")


class UpdatePasswordForm(BaseModel):
    password: str = Field(min_length=6, max_length=64)
    captcha: str = Field(min_length=1, description="验证码")
    captcha_id: str = Field(default="")


@router.put("/password", response_model=R[None], summary="修改密码", description="修改当前登录账号的密码")
async def update_password(
    req_form: UpdatePasswordForm,
    request: Request,
    cuser: AdminUser = Depends(get_current_admin_user),
    redis: aioredis.Redis = Depends(get_redis),
):
    captcha_id = req_form.captcha_id or request.cookies.get("update_password_captcha_id")
    async with redis.client() as conn:
        captcha = await conn.getdel(f"update_password_captcha.{captcha_id}")
        if not captcha or captcha.lower() != req_form.captcha.lower():
            raise ApiException(ApiErrors.ADMIN_CAPTCHA_INCORRECT)
    cuser.salt = random_str(13)
    cuser.password = AdminUser.encrypt_password(req_form.password, cuser.salt, cuser.ptype)
    return R.success(None)


@router.get(
    "/permissions",
    response_model=R[dict[str, bool]],
    summary="查找权限",
    description="判断当前用户是否有权限",
)
async def check_permissions(
    codes: list[str] = Query(min_length=1, description="完整权限代码，诸如 admin.user.create"),
    cuser: AdminUser = Depends(get_current_admin_user),
    system_repo: SystemRepo = Depends(SystemRepo.get),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    m: dict[str, bool] = {}
    for code in codes:
        if cuser.is_superuser:  # 超级管理员拥有所有权限
            m[code] = True
            continue
        permission = await system_repo.get_permission_by_fullcode(code)
        if permission and await admin_repo.check_admin_user_permission(cuser.id, permission.id):
            m[code] = True
        else:
            m[code] = False
    return R.success(m)
