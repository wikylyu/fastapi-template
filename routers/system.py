from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from dal.system import SystemRepo
from database.session import get_db
from middlewares.depends import get_current_admin_user, get_current_super_admin_user
from models.admin import AdminUser
from routers.api import ApiErrors, ApiException
from schemas.response import P, R
from schemas.system import ApiSchema, PermissionSchema, RouteSchema

router = APIRouter()


@router.get("/routes", response_model=R[list[RouteSchema]], summary="查找路由", description="查找路由")
async def find_routes(
    request: Request,
    method: str = Query(default="", description="请求方法"),
    path: str = Query(default="", description="请求路径"),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    app = request.app
    routes = []
    for route in app.routes:
        if path and not route.path.startswith(path):
            continue
        for route_method in route.methods:
            if method and method != route_method:
                continue
            routes.append({"path": route.path, "method": route_method})
    return R.success(routes)


def check_route(method: str, path: str, request: Request) -> bool:
    """
    检查路由是否存在
    """
    app = request.app
    for route in app.routes:
        if method in route.methods and path == route.path:
            return True
    return False


class CreateApiForm(BaseModel):
    method: str = Field(description="请求方法")
    path: str = Field(description="请求路径")
    permission_ids: list[int] = Field(description="权限ID列表", default=[])


@router.post("/api", response_model=R[ApiSchema], summary="创建API", description="创建API")
async def create_api(
    req_form: CreateApiForm,
    request: Request,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    if not check_route(req_form.method, req_form.path, request):
        raise ApiException(ApiErrors.ROUTE_NOT_FOUND)

    api = await SystemRepo.get_api_by_method_and_path(db, req_form.method, req_form.path)
    if api:
        raise ApiException(ApiErrors.API_EXISTS)

    for permission_id in req_form.permission_ids:
        permission = await SystemRepo.get_permission(db, permission_id)
        if not permission:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)

    api = await SystemRepo.create_api(
        db, req_form.method, req_form.path, created_by=cuser.id, permission_ids=req_form.permission_ids
    )

    return R.success(api)


class UpdateApiForm(BaseModel):
    method: str = Field(description="请求方法")
    path: str = Field(description="请求路径")
    permission_ids: list[int] = Field(description="权限ID列表", default=[])


@router.put("/api/{id}", response_model=R[ApiSchema], summary="更新API", description="更新API")
async def update_api(
    id: int,
    req_form: CreateApiForm,
    request: Request,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    if not check_route(req_form.method, req_form.path, request):
        raise ApiException(ApiErrors.ROUTE_NOT_FOUND)

    api = await SystemRepo.get_api_by_method_and_path(db, req_form.method, req_form.path)
    if api and api.id != id:
        raise ApiException(ApiErrors.API_EXISTS)

    api = await SystemRepo.get_api(db, id)
    if not api:
        raise ApiException(ApiErrors.API_NOT_FOUND)

    for permission_id in req_form.permission_ids:
        permission = await SystemRepo.get_permission(db, permission_id)
        if not permission:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)

    api.method = req_form.method
    api.path = req_form.path
    api.permission_ids = req_form.permission_ids
    await db.flush()

    return R.success(api)


@router.delete("/api/{id}", response_model=R[None], summary="删除API", description="删除API")
async def delete_api(
    id: int,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    await SystemRepo.delete_api(db, id)
    return R.success(None)


@router.get("/apis", response_model=R[P[ApiSchema]], summary="查找API", description="查找API")
async def find_apis(
    method: str = Query(default="", description="请求方法"),
    path: str = Query(default="", description="请求路径"),
    page: int = Query(default=1, description="页码"),
    page_size: int = Query(default=10, description="每页条数"),
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    apis, total_count = await SystemRepo.find_apis(db, method, path, page, page_size)
    return R.success(P.from_list(total_count, page, page_size, apis))


class CreatePermissionForm(BaseModel):
    name: str = Field(description="权限名称")
    code: str = Field(description="权限代码")
    parent_id: int = Field(description="父权限ID", default=0)
    remark: str = Field(description="备注", default="")


@router.post("/permission", response_model=R[PermissionSchema], summary="创建权限", description="创建权限")
async def create_permission(
    req_form: CreatePermissionForm,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    if req_form.parent_id:
        parent = await SystemRepo.get_permission(db, req_form.parent_id)
        if not parent:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)
    permission = await SystemRepo.get_permission_by_code_and_parent(db, req_form.code, req_form.parent_id)
    if permission:
        raise ApiException(ApiErrors.PERMISSION_CODE_DUPLICATED)

    permission = await SystemRepo.create_permission(
        db,
        req_form.name,
        req_form.code,
        req_form.remark,
        req_form.parent_id,
        created_by=cuser.id,
    )
    return R.success(permission)


async def check_permission_child(db: AsyncSession, id: int, child_id: int) -> bool:
    """检查child_id是不是id的子权限"""
    if id == child_id:
        print(id, child_id)
        return True
    children = await SystemRepo.find_chilren_permissions_by_parent_r(db, id)
    for child in children:
        if await check_permission_child(db, child.id, child_id):
            return True
    return False


class UpdatePermissionForm(BaseModel):
    name: str = Field(description="权限名称")
    code: str = Field(description="权限代码")
    parent_id: int = Field(description="父权限ID", default=0)
    remark: str = Field(description="备注", default="")


@router.put("/permission/{id}", response_model=R[PermissionSchema], summary="更新权限", description="更新权限")
async def update_permission(
    req_form: UpdatePermissionForm,
    id: int,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    permission = await SystemRepo.get_permission(db, id)
    if not permission:
        raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)

    if req_form.parent_id:
        parent = await SystemRepo.get_permission(db, req_form.parent_id)
        if not parent:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)

        if await check_permission_child(db, id, req_form.parent_id):
            raise ApiException(ApiErrors.PERMISSION_PARENT_INVALID)

    other = await SystemRepo.get_permission_by_code_and_parent(db, req_form.code, req_form.parent_id)
    if other and other.id != id:
        raise ApiException(ApiErrors.PERMISSION_CODE_DUPLICATED)

    permission.name = req_form.name
    permission.code = req_form.code
    permission.parent_id = req_form.parent_id
    permission.remark = req_form.remark
    await db.flush()

    return R.success(permission)


@router.get("/permissions", response_model=R[list[PermissionSchema]], summary="查找权限", description="查找权限")
async def find_permissions(
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_admin_user),
):
    permissions = await SystemRepo.find_chilren_permissions_by_parent_r(db, parent_id=0)
    return R.success(permissions)


@router.delete(
    "/permission/{id}",
    response_model=R[None],
    summary="删除权限",
    description="删除权限，会删除所有子权限，并且从API山移除对应权限",
)
async def delete_permission(
    id: int,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    await SystemRepo.delete_permission(db, id)
    return R.success(None)


class UpdatePermissionSortForm(BaseModel):
    sort: int = Field(description="排序")


@router.put("/permission/{id}/sort", response_model=R[None], summary="权限排序", description="权限排序")
async def update_permission_sort(
    id: int,
    req_form: UpdatePermissionSortForm,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    await SystemRepo.update_permission_sort(db, id, req_form.sort)
    return R.success(None)


@router.get("/permission/{id}", response_model=R[list[PermissionSchema]], summary="权限详情", description="权限详情")
async def find_permission(
    id: int,
    db: AsyncSession = Depends(get_db),
    cuser: AdminUser = Depends(get_current_admin_user),
):
    permissions = []
    while id > 0:
        permission = await SystemRepo.get_permission(db, id)
        if not permission:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)
        permissions.append(permission)
        id = permission.parent_id
    permissions.reverse()
    return R.success(permissions)
