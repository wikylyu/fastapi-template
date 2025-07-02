from functools import lru_cache

from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from fastapi.routing import APIRoute
from sqlalchemy.ext.asyncio import AsyncSession

from dal.admin import AdminRepo
from dal.system import SystemRepo
from database.session import get_db
from models.admin import AdminUser, AdminUserStatus, AdminUserToken, AdminUserTokenStatus
from services.encrypt import EncryptService, get_encrypt_service


@lru_cache()
def get_route_map(app):
    route_map = {}
    for route in app.routes:
        if isinstance(route, APIRoute):
            route_map[route.endpoint] = route.path
    return route_map


def get_current_route(request: Request) -> dict[str, str]:
    """获取当前的路由"""
    method = request.method
    endpoint = request.scope["endpoint"]
    path = get_route_map(request.app).get(endpoint, request.scope["path"])
    return method, path


async def get_auth_token(
    admin_user_token: str | None = Cookie(default=None),
    authorization: str | None = Header(default=None),
    encrypt_service: EncryptService = Depends(get_encrypt_service),
) -> str | None:
    """从Cookie或Header中获取token"""
    token = None
    if admin_user_token:
        token = admin_user_token
    if authorization:
        scheme, _, t = authorization.partition(" ")
        if scheme.lower() == "bearer":
            token = t
    if not token:
        return None
    try:
        return encrypt_service.decrypt(token)
    except Exception:
        return None


async def try_current_admin_user_token(
    token: str | None = Depends(get_auth_token),
    db: AsyncSession = Depends(get_db),
) -> AdminUserToken | None:
    if not token:
        return None
    admin_user_token = await AdminRepo.get_admin_user_token(db, token)
    if (
        not admin_user_token
        or admin_user_token.status != AdminUserTokenStatus.ACTIVE.value
        or admin_user_token.is_expired()
    ):
        return None
    return admin_user_token


async def try_current_admin_user(
    admin_user_token: AdminUserToken | None = Depends(try_current_admin_user_token),
) -> AdminUser | None:
    if not admin_user_token:
        return None
    admin_user = admin_user_token.admin_user
    if admin_user and admin_user.status != AdminUserStatus.ACTIVE.value:
        return None
    return admin_user


async def get_current_admin_user(
    admin_user: AdminUser | None = Depends(try_current_admin_user),
    route=Depends(get_current_route),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    if not admin_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    if not admin_user.is_superuser:  # 不是超级管理员则检查权限
        method = route[0]
        path = route[1]
        api = await SystemRepo.get_api_by_method_and_path(db, method, path)
        if api:  # 只有存在该Api的时候才检查权限
            is_granted = await AdminRepo.check_admin_user_permission(db, admin_user.id, *api.permission_ids)
            if not is_granted:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return admin_user


async def get_current_super_admin_user(
    admin_user: AdminUser = Depends(get_current_admin_user),
) -> AdminUser:
    if not admin_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return admin_user


async def get_client_real_ip(
    request: Request,
    x_forwarded_for: str | None = Header(default=None),
    x_real_ip: str | None = Header(default=None),
    cf_connecting_ip: str | None = Header(default=None),
) -> str:
    """
    获取客户端真实 IP 地址，考虑以下情况：
    - 直接连接：使用 request.client.host
    - 代理服务器：检查 X-Forwarded-For 或 X-Real-IP
    - Cloudflare：优先使用 CF-Connecting-IP
    """
    # 优先级 1：Cloudflare 的 CF-Connecting-IP
    if cf_connecting_ip:
        return cf_connecting_ip

    # 优先级 2：X-Forwarded-For（代理链中的第一个 IP）
    if x_forwarded_for:
        # X-Forwarded-For 可能包含多个 IP，取第一个（客户端 IP）
        return x_forwarded_for.split(",")[0].strip()

    # 优先级 3：X-Real-IP（某些代理设置的单一 IP）
    if x_real_ip:
        return x_real_ip

    # 默认：直接使用 request.client.host（无代理或代理未正确配置）
    return request.client.host
