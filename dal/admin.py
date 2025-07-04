import random
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from dal.base import BaseRepo
from models.admin import (
    AdminRole,
    AdminUser,
    AdminUserRole,
    AdminUserStatus,
    AdminUserToken,
    AdminUserTokenStatus,
    PasswordType,
)
from utils.string import random_str


class AdminRepo(BaseRepo):
    @classmethod
    def random_ptype(cls) -> str:
        return random.choice([PasswordType.MD5.value, PasswordType.SHA256.value, PasswordType.SHA512.value])

    @classmethod
    async def get_admin_user(cls, db: AsyncSession, id: int) -> AdminUser | None:
        r = await db.execute(select(AdminUser).where(AdminUser.id == id))
        return r.scalars().first()

    @classmethod
    async def get_admin_user_by_username(cls, db: AsyncSession, username: str) -> AdminUser | None:
        """根据用户名获取管理员用户"""
        r = await db.execute(select(AdminUser).where(AdminUser.username == username))
        return r.scalars().first()

    @classmethod
    async def check_super_admin_user_exists(cls, db: AsyncSession):
        """检查是否存在超级管理员用户"""
        r = await db.execute(select(AdminUser).where(AdminUser.is_superuser))
        return r.scalars().first()

    @classmethod
    async def create_admin_user(
        cls,
        db: AsyncSession,
        username: str,
        name: str,
        password: str,
        status: str = AdminUserStatus.ACTIVE.value,
        is_superuser: bool = False,
        email: str = "",
        phone: str = "",
        created_by: int = 0,
    ) -> AdminUser:
        salt = random_str(13)
        ptype = cls.random_ptype()
        password = AdminUser.encrypt_password(password, salt, ptype)
        admin_user = AdminUser(
            username=username,
            name=name,
            password=password,
            salt=salt,
            ptype=ptype,
            status=status,
            is_superuser=is_superuser,
            email=email,
            phone=phone,
            created_by=created_by,
        )
        db.add(admin_user)
        await db.flush()
        return admin_user

    @classmethod
    async def create_admin_user_token(
        cls,
        db: AsyncSession,
        admin_user_id: int,
        expired_at: datetime | None = None,
        ip: str = "",
        user_agent: str = "",
    ):
        admin_user_token = AdminUserToken(
            admin_user_id=admin_user_id,
            status=AdminUserTokenStatus.ACTIVE.value,
            expired_at=expired_at,
            ip=ip,
            user_agent=user_agent,
        )
        db.add(admin_user_token)
        await db.flush()
        return admin_user_token

    @classmethod
    async def get_admin_user_token(cls, db: AsyncSession, token: str) -> AdminUserToken | None:
        r = await db.execute(
            select(AdminUserToken).options(joinedload(AdminUserToken.admin_user)).where(AdminUserToken.id == token)
        )
        return r.scalars().first()

    @classmethod
    async def find_admin_users(
        cls, db: AsyncSession, query: str = "", status: str = "", page: int = 1, page_size: int = 10
    ) -> tuple[list[AdminUser], int]:
        q = select(AdminUser).order_by(AdminUser.created_at.desc())
        if query:
            q = q.where((AdminUser.name.contains(query)) | (AdminUser.username.contains(query)))
        if status:
            q = q.where(AdminUser.status == status)

        return await cls._query_pagination(db, q, page, page_size)

    @classmethod
    async def get_admin_role(cls, db: AsyncSession, id: int) -> AdminRole | None:
        r = await db.execute(select(AdminRole).where(AdminRole.id == id))
        return r.scalars().first()

    @classmethod
    async def create_admin_role(
        cls, db: AsyncSession, name: str, remark: str, permission_ids: list[int], created_by: int
    ):
        role = AdminRole(name=name, remark=remark, permission_ids=permission_ids, created_by=created_by)
        db.add(role)
        await db.flush()
        return role

    @classmethod
    async def find_admin_roles(cls, db: AsyncSession, query: str = "", page: int = 1, page_size: int = 10):
        q = select(AdminRole).order_by(AdminRole.created_at.desc())
        if query:
            q = q.where(AdminRole.name.contains(query))

        return await cls._query_pagination(db, q, page, page_size)

    @classmethod
    async def create_admin_user_role(cls, db: AsyncSession, admin_user_id: int, admin_role_id: int) -> AdminUserRole:
        admin_user_role = AdminUserRole(admin_user_id=admin_user_id, admin_role_id=admin_role_id)
        db.add(admin_user_role)
        await db.flush()
        return admin_user_role

    @classmethod
    async def delete_admin_user_role_by_user_id(cls, db: AsyncSession, admin_user_id: int):
        await db.execute(delete(AdminUserRole).where(AdminUserRole.admin_user_id == admin_user_id))

    @classmethod
    async def find_admin_user_roles(cls, db: AsyncSession, admin_user_id: int) -> list[AdminRole]:
        r = await db.execute(
            select(AdminRole)
            .join(AdminUserRole, AdminUserRole.admin_role_id == AdminRole.id)
            .where(AdminUserRole.admin_user_id == admin_user_id)
            .order_by(AdminUserRole.created_at.asc())
        )
        return r.scalars().all()

    @classmethod
    async def check_admin_user_permission(cls, db: AsyncSession, admin_user_id: int, *permission_ids: int) -> bool:
        """判断用户是否拥有权限"""
        if not permission_ids:
            return True
        r = await db.execute(
            select(AdminRole)
            .join(AdminUserRole, AdminUserRole.admin_role_id == AdminRole.id)
            .where(
                AdminUserRole.admin_user_id == admin_user_id,
            )
            .where(AdminRole.permission_ids.overlap(permission_ids))
        )
        return bool(r.scalars().first())
