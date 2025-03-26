from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from config import ADMIN_USERNAME_PATTERN
from dal.admin import AdminRepo
from database.session import get_db
from middlewares.depends import get_current_admin_user
from models.admin import AdminUser, AdminUserStatus
from routers.api import ApiErrors, ApiException
from schemas.admin import AdminUserSchema
from schemas.response import P, R
from utils.string import random_str

router = APIRouter()


@router.get("/user/{id}", response_model=R[AdminUserSchema], summary="获取用户详情", description="通过ID获取用户详情")
async def get_admin_user(
    id: int, db: AsyncSession = Depends(get_db), admin_user: AdminUser = Depends(get_current_admin_user)
):
    user = await AdminRepo.get_admin_user(db, id)
    if not user:
        raise ApiException(ApiErrors.ADMIN_USER_NOT_FOUND)
    return R.success(user)


@router.get("/users", response_model=R[P[AdminUserSchema]], summary="获取用户列表", description="获取用户列表")
async def find_admin_users(
    query: str = Query(default=""),
    status: str = Query(default=""),
    page: int = Query(default=1, min=1),
    page_size: int = Query(default=10, min=1, max=100),
    db: AsyncSession = Depends(get_db),
    admin_user: AdminUser = Depends(get_current_admin_user),
):
    admin_users, total_count = await AdminRepo.find_admin_users(db, query, status, page, page_size)
    return R.success(P.from_list(total_count, page, page_size, admin_users))


class CreateAdminUserForm(BaseModel):
    username: str = Field(min_length=4, max_length=32, pattern=ADMIN_USERNAME_PATTERN)
    password: str = Field(min_length=6, max_length=64)
    name: str = Field(min_length=1, max_length=64)
    email: str = Field(max_length=64)
    phone: str = Field(max_length=32)
    status: AdminUserStatus = Field(default=AdminUserStatus.ACTIVE, description="用户状态")


@router.post("/user", response_model=R[AdminUserSchema], summary="创建用户", description="创建用户")
async def create_admin_user(
    req_form: CreateAdminUserForm,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_admin_user),
):
    admin_user = await AdminRepo.get_admin_user_by_username(db, req_form.username)
    if admin_user:  # 用户名重复
        raise ApiException(ApiErrors.ADMIN_USER_DUPLICATED)
    admin_user = await AdminRepo.create_admin_user(
        db,
        req_form.username,
        req_form.name,
        req_form.password,
        status=req_form.status.value,
        email=req_form.email,
        phone=req_form.phone,
        created_by=cuser.id,
    )
    return R.success(admin_user)


class UpdateAdminUserForm(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    email: str = Field(max_length=64)
    phone: str = Field(max_length=32)
    password: str = Field(default="", description="如何有密码，则重置密码，否则忽略")
    status: AdminUserStatus = Field(default=AdminUserStatus.ACTIVE, description="用户状态")


@router.put("/user/{id}", response_model=R[AdminUserSchema], summary="更新用户", description="更新用户")
async def update_admin_user(
    id: int,
    req_form: UpdateAdminUserForm,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_admin_user),
):
    admin_user = await AdminRepo.get_admin_user(db, id)
    if not admin_user:
        raise ApiException(ApiErrors.ADMIN_USER_NOT_FOUND)
    admin_user.name = req_form.name
    admin_user.email = req_form.email
    admin_user.phone = req_form.phone
    admin_user.status = req_form.status.value
    if req_form.password:
        admin_user.salt = random_str(12)
        admin_user.password = AdminUser.encrypt_password(req_form.password, admin_user.salt, admin_user.ptype)
    await db.flush()
    return R.success(admin_user)
