from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dal.admin import AdminRepo
from database.session import get_db
from middlewares.depends import get_current_admin_user
from models.admin import AdminUser
from routers.api import ApiErrors, ApiException
from schemas.admin import AdminUserSchema
from schemas.response import P, R

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
