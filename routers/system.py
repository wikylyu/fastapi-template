from fastapi import APIRouter, Query, Request

from schemas.response import R
from schemas.system import Endpoint

router = APIRouter()


@router.get("/endpoints", response_model=R[list[Endpoint]], summary="查找路由", description="查找路由")
async def find_endpoints(
    request: Request,
    method: str = Query(default="", description="请求方法"),
    path: str = Query(default="", description="请求路径"),
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
