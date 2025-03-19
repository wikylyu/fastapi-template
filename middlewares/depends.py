from fastapi import Cookie, Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dal.admin import AdminRepo
from database.session import get_db
from models.admin import AdminUser, AdminUserToken, AdminUserTokenStatus
from services.encrypt import encrypt_service


async def get_auth_token(
    admin_user_token: str | None = Cookie(default=None), authorization: str | None = Header(default=None)
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


async def get_admin_user_token(
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


async def try_admin_user(
    admin_user_token: AdminUserToken | None = Depends(get_admin_user_token),
) -> AdminUser | None:
    if not admin_user_token:
        return None
    return admin_user_token.admin_user


async def get_admin_user(
    admin_user: AdminUser | None = Depends(try_admin_user),
) -> AdminUser:
    if not admin_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return admin_user
