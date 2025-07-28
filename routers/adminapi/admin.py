from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field

from config import ADMIN_USERNAME_PATTERN
from dal.admin import AdminRepo
from dal.system import SystemRepo
from middlewares.depends import get_current_admin_user
from models.admin import AdminUser, AdminUserStatus
from routers.adminapi.schemas.admin import AdminRoleSchema, AdminUserSchema
from routers.api import ApiErrors, ApiException
from routers.response import P, R
from utils.string import random_str

router = APIRouter()


@router.get("/user/{id}", response_model=R[AdminUserSchema], summary="获取用户详情", description="通过ID获取用户详情")
async def get_admin_user(
    id: int,
    cuser: AdminUser = Depends(get_current_admin_user),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    user = await admin_repo.get_admin_user(id)
    if not user:
        raise ApiException(ApiErrors.ADMIN_USER_NOT_FOUND)
    return R.success(user)


@router.get("/users", response_model=R[P[AdminUserSchema]], summary="获取用户列表", description="获取用户列表")
async def find_admin_users(
    query: str = Query(default=""),
    status: str = Query(default=""),
    page: int = Query(default=1, min=1),
    page_size: int = Query(default=10, min=1, max=100),
    cuser: AdminUser = Depends(get_current_admin_user),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    admin_users, total_count = await admin_repo.find_admin_users(query, status, page, page_size)
    return R.success(P.from_list(total_count, page, page_size, admin_users))


class CreateAdminUserForm(BaseModel):
    username: str = Field(min_length=4, max_length=32, pattern=ADMIN_USERNAME_PATTERN)
    password: str = Field(min_length=6, max_length=64)
    name: str = Field(min_length=1, max_length=64)
    email: str = Field(max_length=64)
    phone: str = Field(max_length=32)
    status: AdminUserStatus = Field(default=AdminUserStatus.ACTIVE, description="用户状态")

    role_ids: list[int] = Field(default=[], description="角色ID列表")


@router.post("/user", response_model=R[AdminUserSchema], summary="创建用户", description="创建用户")
async def create_admin_user(
    req_form: CreateAdminUserForm,
    cuser: AdminUser = Depends(get_current_admin_user),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    admin_user = await admin_repo.get_admin_user_by_username(req_form.username)
    if admin_user:  # 用户名重复
        raise ApiException(ApiErrors.ADMIN_USER_DUPLICATED)
    admin_user = await admin_repo.create_admin_user(
        req_form.username,
        req_form.name,
        req_form.password,
        status=req_form.status.value,
        email=req_form.email,
        phone=req_form.phone,
        created_by=cuser.id,
    )
    for role_id in req_form.role_ids:
        role = await admin_repo.get_admin_role(role_id)  # 检查角色是否存在
        if not role:
            raise ApiException(ApiErrors.ADMIN_ROLE_NOT_FOUND)
        await admin_repo.create_admin_user_role(admin_user.id, role.id)
    return R.success(admin_user)


class UpdateAdminUserForm(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    email: str = Field(max_length=64)
    phone: str = Field(max_length=32)
    password: str = Field(default="", description="如何有密码，则重置密码，否则忽略")
    status: AdminUserStatus = Field(default=AdminUserStatus.ACTIVE, description="用户状态")

    role_ids: list[int] = Field(default=[], description="角色ID列表")


@router.put("/user/{id}", response_model=R[AdminUserSchema], summary="更新用户", description="更新用户")
async def update_admin_user(
    id: int,
    req_form: UpdateAdminUserForm,
    cuser: AdminUser = Depends(get_current_admin_user),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    admin_user = await admin_repo.get_admin_user(id)
    if not admin_user:
        raise ApiException(ApiErrors.ADMIN_USER_NOT_FOUND)
    admin_user.name = req_form.name
    admin_user.email = req_form.email
    admin_user.phone = req_form.phone
    admin_user.status = req_form.status.value
    if req_form.password:
        admin_user.salt = random_str(12)
        admin_user.password = AdminUser.encrypt_password(req_form.password, admin_user.salt, admin_user.ptype)

    await admin_repo.delete_admin_user_role_by_user_id(admin_user.id)
    for role_id in req_form.role_ids:
        role = await admin_repo.get_admin_role(role_id)  # 检查角色是否存在
        if not role:
            raise ApiException(ApiErrors.ADMIN_ROLE_NOT_FOUND)
        await admin_repo.create_admin_user_role(admin_user.id, role.id)

    return R.success(admin_user)


@router.get(
    "/user/{id}/roles",
    response_model=R[list[AdminRoleSchema]],
    summary="获取用户角色列表",
    description="获取用户角色列表",
)
async def find_admin_user_roles(
    id: int,
    cuser: AdminUser = Depends(get_current_admin_user),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    roles = await admin_repo.find_admin_user_roles(id)
    return R.success(roles)


class CreateAdminRoleForm(BaseModel):
    name: str = Field(min_length=1, max_length=64, description="角色名称")
    remark: str = Field(default="", description="备注")
    permission_ids: list[int] = Field(default=[], description="权限ID列表")


@router.post("/role", response_model=R[AdminRoleSchema], summary="创建角色", description="创建角色")
async def create_admin_role(
    req_form: CreateAdminRoleForm,
    cuser: AdminUser = Depends(get_current_admin_user),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
    system_repo: SystemRepo = Depends(SystemRepo.get),
):
    for permission_id in req_form.permission_ids:
        permission = await system_repo.get_permission(permission_id)
        if not permission:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)
    admin_role = await admin_repo.create_admin_role(
        req_form.name, req_form.remark, req_form.permission_ids, created_by=cuser.id
    )
    return R.success(admin_role)


class UpdateAdminRoleForm(BaseModel):
    name: str = Field(min_length=1, max_length=64, description="角色名称")
    remark: str = Field(default="", description="备注")
    permission_ids: list[int] = Field(default=[], description="权限ID列表")


@router.put("/role/{id}", response_model=R[AdminRoleSchema], summary="更新角色", description="更新角色")
async def update_admin_role(
    id: int,
    req_form: UpdateAdminRoleForm,
    admin_repo: AdminRepo = Depends(AdminRepo.get),
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_admin_user),
):
    admin_role = await admin_repo.get_admin_role(id)
    if not admin_role:
        raise ApiException(ApiErrors.ADMIN_ROLE_NOT_FOUND)
    for permission_id in req_form.permission_ids:
        permission = await system_repo.get_permission(permission_id)
        if not permission:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)
    admin_role.name = req_form.name
    admin_role.remark = req_form.remark
    admin_role.permission_ids = req_form.permission_ids
    return R.success(admin_role)


@router.get("/roles", response_model=R[P[AdminRoleSchema]], summary="获取角色列表", description="获取角色列表")
async def find_admin_roles(
    query: str = Query(default=""),
    page: int = Query(default=1, min=1),
    page_size: int = Query(default=10, min=1, max=100),
    cuser: AdminUser = Depends(get_current_admin_user),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    admin_roles, total_count = await admin_repo.find_admin_roles(query, page, page_size)
    return R.success(P.from_list(total_count, page, page_size, admin_roles))


@router.get("/role/{id}", response_model=R[AdminRoleSchema], summary="获取角色详情", description="通过ID获取角色详情")
async def get_admin_role(
    id: int,
    cuser: AdminUser = Depends(get_current_admin_user),
    admin_repo: AdminRepo = Depends(AdminRepo.get),
):
    role = await admin_repo.get_admin_role(id)
    if not role:
        raise ApiException(ApiErrors.ADMIN_ROLE_NOT_FOUND)
    return R.success(role)
