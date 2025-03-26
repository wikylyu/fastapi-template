from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

from models.base import BaseTable
from utils.password import encrypt_password_md5, encrypt_password_sha256, encrypt_password_sha512
from utils.uuid import uuidv4


class PasswordType(Enum):
    MD5 = "md5"
    SHA256 = "sha256"
    SHA512 = "sha512"


class AdminUserStatus(Enum):
    ACTIVE = "active"
    BANNED = "banned"


class AdminUser(BaseTable):
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    username: str = Column(String(32), unique=True, nullable=False)  # 登录名，用于登录
    name: str = Column(String(64), nullable=False, default="")  # 姓名
    email: str = Column(String(64), nullable=False, default="")  # 邮箱
    phone: str = Column(String(32), nullable=False, default="")  # 手机号

    password: str = Column(String(256), nullable=False, default="")  # 加密后的密码
    salt: str = Column(String(32), nullable=False, default="")  # 密码加密的盐
    ptype: str = Column(String(32), nullable=False, default="")  # 密码加密方式

    status: str = Column(String(32), nullable=False, default=AdminUserStatus.ACTIVE.value, index=True)

    is_superuser: bool = Column(Boolean, nullable=False, default=False)  # 是否是超级管理员
    created_by: int = Column(Integer, nullable=False, index=True, default=0, server_default="0")

    __table_args__ = (
        Index("idx_username_trgm", "username", postgresql_using="gin", postgresql_ops={"username": "gin_trgm_ops"}),
        Index("idx_name_trgm", "name", postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"}),
    )

    def auth(self, password: str) -> bool:
        if not self.password:
            return False
        if self.ptype == PasswordType.MD5.value:
            return self.password == encrypt_password_md5(password, self.salt)
        elif self.ptype == PasswordType.SHA256.value:
            return self.password == encrypt_password_sha256(password, self.salt)
        elif self.ptype == PasswordType.SHA512.value:
            return self.password == encrypt_password_sha512(password, self.salt)
        else:
            return False

    @classmethod
    def encrypt_password(cls, password: str, salt: str, ptype: str):
        if ptype == PasswordType.MD5.value:
            return encrypt_password_md5(password, salt)
        elif ptype == PasswordType.SHA256.value:
            return encrypt_password_sha256(password, salt)
        elif ptype == PasswordType.SHA512.value:
            return encrypt_password_sha512(password, salt)


class AdminUserTokenStatus(Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class AdminUserToken(BaseTable):
    id: str = Column(String, primary_key=True, default=uuidv4)
    admin_user_id: int = Column(Integer, index=True, nullable=False)
    status: str = Column(String(32), index=True, nullable=False, default=AdminUserTokenStatus.ACTIVE.value)
    expired_at: datetime | None = Column(DateTime, nullable=True)
    ip: str = Column(String(128), nullable=False, default="")
    user_agent: str = Column(String(512), nullable=False, default="")

    admin_user: AdminUser | None = relationship(
        "AdminUser", primaryjoin="AdminUser.id == foreign(AdminUserToken.admin_user_id)"
    )

    def is_expired(self) -> bool:
        return self.expired_at and self.expired_at < datetime.now()


class AdminRole(BaseTable):
    id: int = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String(64), nullable=False)
    remark: str = Column(String(256), nullable=False)
    permission_ids = Column(ARRAY(Integer), nullable=False, default=[])
    created_by: int = Column(
        Integer,
        nullable=False,
        index=True,
    )

    __table_args__ = (  # 设置method和path的联合unique
        Index("idx_admin_role__permission_ids_gin", "permission_ids", postgresql_using="gin"),
    )
