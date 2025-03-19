import random

from sqlalchemy.orm import Session

from models.admin import AdminUser, AdminUserStatus, PasswordType
from utils.string import random_str


class AdminRepo:
    @classmethod
    def random_ptype(cls) -> str:
        return random.choice([PasswordType.MD5.value, PasswordType.SHA256.value, PasswordType.SHA512.value])

    @classmethod
    def get_admin_user_by_username(cls, db: Session, username: str):
        """根据用户名获取管理员用户"""
        return db.query(AdminUser).filter(AdminUser.username == username).first()

    @classmethod
    def check_super_admin_user_exists(cls, db: Session):
        """检查是否存在超级管理员用户"""
        return db.query(AdminUser).filter(AdminUser.is_superuser).first()

    @classmethod
    def create_admin_user(
        cls,
        db: Session,
        username: str,
        name: str,
        password: str,
        status: str = AdminUserStatus.ACTIVE.value,
        is_superuser: bool = False,
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
        )
        db.add(admin_user)
        db.flush()
        return admin_user
