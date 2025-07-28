from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, Field

from dal.system import SystemRepo
from middlewares.depends import get_current_admin_user, get_current_super_admin_user
from models.admin import AdminUser
from routers.adminapi.schemas.system import ApiSchema, PermissionSchema, RouteSchema
from routers.api import ApiErrors, ApiException
from routers.response import P, R

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
        if not route.path.startswith("/adminapi/"):
            continue
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
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    if not check_route(req_form.method, req_form.path, request):
        raise ApiException(ApiErrors.ROUTE_NOT_FOUND)

    api = await system_repo.get_api_by_method_and_path(req_form.method, req_form.path)
    if api:
        raise ApiException(ApiErrors.API_EXISTS)

    for permission_id in req_form.permission_ids:
        permission = await system_repo.get_permission(permission_id)
        if not permission:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)

    api = await system_repo.create_api(
        req_form.method, req_form.path, created_by=cuser.id, permission_ids=req_form.permission_ids
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
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    if not check_route(req_form.method, req_form.path, request):
        raise ApiException(ApiErrors.ROUTE_NOT_FOUND)

    api = await system_repo.get_api_by_method_and_path(req_form.method, req_form.path)
    if api and api.id != id:
        raise ApiException(ApiErrors.API_EXISTS)

    api = await system_repo.get_api(id)
    if not api:
        raise ApiException(ApiErrors.API_NOT_FOUND)

    for permission_id in req_form.permission_ids:
        permission = await system_repo.get_permission(permission_id)
        if not permission:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)

    api.method = req_form.method
    api.path = req_form.path
    api.permission_ids = req_form.permission_ids

    return R.success(api)


@router.delete("/api/{id}", response_model=R[None], summary="删除API", description="删除API")
async def delete_api(
    id: int,
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    await system_repo.delete_api(id)
    return R.success(None)


@router.get("/apis", response_model=R[P[ApiSchema]], summary="查找API", description="查找API")
async def find_apis(
    method: str = Query(default="", description="请求方法"),
    path: str = Query(default="", description="请求路径"),
    page: int = Query(default=1, description="页码"),
    page_size: int = Query(default=10, description="每页条数"),
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    apis, total_count = await system_repo.find_apis(method, path, page, page_size)
    return R.success(P.from_list(total_count, page, page_size, apis))


class CreatePermissionForm(BaseModel):
    name: str = Field(description="权限名称")
    code: str = Field(description="权限代码")
    parent_id: int = Field(description="父权限ID", default=0)
    remark: str = Field(description="备注", default="")


@router.post("/permission", response_model=R[PermissionSchema], summary="创建权限", description="创建权限")
async def create_permission(
    req_form: CreatePermissionForm,
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    if req_form.parent_id:
        parent = await system_repo.get_permission(req_form.parent_id)
        if not parent:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)
    permission = await system_repo.get_permission_by_code_and_parent(req_form.code, req_form.parent_id)
    if permission:
        raise ApiException(ApiErrors.PERMISSION_CODE_DUPLICATED)

    permission = await system_repo.create_permission(
        req_form.name,
        req_form.code,
        req_form.remark,
        req_form.parent_id,
        created_by=cuser.id,
    )
    return R.success(permission)


async def check_permission_child(system_repo: SystemRepo, id: int, child_id: int) -> bool:
    """检查child_id是不是id的子权限"""
    if id == child_id:
        print(id, child_id)
        return True
    children = await system_repo.find_chilren_permissions_by_parent_r(id)
    for child in children:
        if await check_permission_child(system_repo, child.id, child_id):
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
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    permission = await system_repo.get_permission(id)
    if not permission:
        raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)

    if req_form.parent_id:
        parent = await system_repo.get_permission(req_form.parent_id)
        if not parent:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)

        if await check_permission_child(system_repo, id, req_form.parent_id):
            raise ApiException(ApiErrors.PERMISSION_PARENT_INVALID)

    other = await system_repo.get_permission_by_code_and_parent(req_form.code, req_form.parent_id)
    if other and other.id != id:
        raise ApiException(ApiErrors.PERMISSION_CODE_DUPLICATED)

    permission.name = req_form.name
    permission.code = req_form.code
    permission.parent_id = req_form.parent_id
    permission.remark = req_form.remark

    return R.success(permission)


@router.get("/permissions", response_model=R[list[PermissionSchema]], summary="查找权限", description="查找权限")
async def find_permissions(
    cuser: AdminUser = Depends(get_current_admin_user),
    system_repo: SystemRepo = Depends(SystemRepo.get),
):
    permissions = await system_repo.find_chilren_permissions_by_parent_r(parent_id=0)
    return R.success(permissions)


@router.delete(
    "/permission/{id}",
    response_model=R[None],
    summary="删除权限",
    description="删除权限，会删除所有子权限，并且从API山移除对应权限",
)
async def delete_permission(
    id: int,
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    await system_repo.delete_permission(id)
    return R.success(None)


class UpdatePermissionSortForm(BaseModel):
    sort: int = Field(description="排序")


@router.put("/permission/{id}/sort", response_model=R[None], summary="权限排序", description="权限排序")
async def update_permission_sort(
    id: int,
    req_form: UpdatePermissionSortForm,
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_super_admin_user),
):
    await system_repo.update_permission_sort(id, req_form.sort)
    return R.success(None)


@router.get("/permission/{id}", response_model=R[list[PermissionSchema]], summary="权限详情", description="权限详情")
async def find_permission(
    id: int,
    system_repo: SystemRepo = Depends(SystemRepo.get),
    cuser: AdminUser = Depends(get_current_admin_user),
):
    permissions = []
    while id > 0:
        permission = await system_repo.get_permission(id)
        if not permission:
            raise ApiException(ApiErrors.PERMISSION_NOT_FOUND)
        permissions.append(permission)
        id = permission.parent_id
    permissions.reverse()
    return R.success(permissions)
