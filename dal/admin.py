import random
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from models.admin import AdminUser, AdminUserStatus, AdminUserToken, AdminUserTokenStatus, PasswordType
from utils.string import random_str


class AdminRepo:
    @classmethod
    def random_ptype(cls) -> str:
        return random.choice([PasswordType.MD5.value, PasswordType.SHA256.value, PasswordType.SHA512.value])

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
        )
        db.add(admin_user)
        await db.flush()
        return admin_user

    @classmethod
    async def create_admin_user_token(cls, db: AsyncSession, admin_user_id: int, expired_at: datetime | None = None):
        admin_user_token = AdminUserToken(
            admin_user_id=admin_user_id,
            status=AdminUserTokenStatus.ACTIVE.value,
            expired_at=expired_at,
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
