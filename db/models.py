from db.psql import TableBase
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
import random
import string
import hashlib


class UserStatus(enum.Enum):
    OK = 'OK'
    Banned = 'Banned'


class UserTokenStatus(enum.Enum):
    OK = 'OK'
    Invalid = 'Invalid'


class PasswordType(enum.Enum):
    MD5 = "MD5"
    SHA256 = "SHA256"
    SHA1 = "SHA1"


def random_password_type() -> PasswordType:
    return random.choice(
        [PasswordType.MD5, PasswordType.SHA256, PasswordType.SHA1])


def random_salt() -> str:
    return ''.join(random.choice(string.ascii_letters) for i in range(10))


def encrypt_password(ptype: PasswordType, salt: str, plain: str):
    password = '{}*{}^'.format(salt, plain)
    m = hashlib.md5()
    if ptype == PasswordType.SHA256:
        m = hashlib.sha256()
        m = hashlib.sha1()
    m.update(password.encode())
    return m.hexdigest()


class User(TableBase):
    __incomplete_tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nickname = Column(String, index=True, nullable=False, default='')
    phone = Column(String, index=True, unique=True, nullable=False, default='')
    avatar = Column(String, nullable=False, default='')
    gender = Column(String, nullable=False, default='')
    status = Column(Enum(UserStatus), nullable=False,
                    index=True, default=UserStatus.OK)
    wxopenid = Column(String, nullable=False, default='')
    wxunionid = Column(String, nullable=False, default='')
    salt = Column(String, nullable=False, default='')
    password = Column(String, nullable=False, default='')
    ptype = Column(Enum(PasswordType), nullable=False)

    created_time = Column(DateTime(timezone=True), server_default=func.now())
    updated_time = Column(DateTime(timezone=True),
                          onupdate=func.now(), server_default=func.now())

    def check_password(self, plain: str) -> bool:
        '''检查密码是否正确'''
        return self.password and encrypt_password(self.ptype, self.salt, plain) == self.password


class UserToken(TableBase):
    __incomplete_tablename__ = "user_token"

    id = Column(String, primary_key=True, index=True,
                server_default='uuid_generate_v4()')
    user_id = Column(Integer, ForeignKey(User.id), index=True)
    device = Column(String, default='')
    method = Column(String, default='')
    ip = Column(String, default='')
    expired_time = Column(DateTime(timezone=True), nullable=True, default=None)
    status = Column(Enum(UserTokenStatus), index=True)
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    updated_time = Column(DateTime(timezone=True),
                          onupdate=func.now(), server_default=func.now())

    user = relationship('User')


class AdminStaffStatus(enum.Enum):

    OK = "OK"
    Banned = "Banned"


class AdminStaff(TableBase):
    __incomplete_tablename__ = 'admin_staff'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True)
    name = Column(String, default='')
    phone = Column(String, default='')
    email = Column(String, default='')
    salt = Column(String, nullable=False, default='')
    password = Column(String, nullable=False, default='')
    ptype = Column(Enum(PasswordType), nullable=False)
    status = Column(Enum(AdminStaffStatus), nullable=False,
                    default=AdminStaffStatus.OK,)

    is_superuser = Column(Boolean, default=False)
    created_by = Column(Integer, default=0)
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    updated_time = Column(DateTime(timezone=True),
                          onupdate=func.now(), server_default=func.now())

    def check_password(self, plain: str) -> bool:
        return self.password and encrypt_password(self.ptype, self.salt, plain) == self.password


class AdminStaffTokenStatus(enum.Enum):

    OK = "OK"
    Invalid = "Invalid"


class AdminStaffToken(TableBase):
    __incomplete_tablename__ = "admin_staff_token"

    id = Column(String, primary_key=True, index=True,
                server_default='uuid_generate_v4()')
    staff_id = Column(Integer, ForeignKey(AdminStaff.id), index=True)
    device = Column(String, default='')
    ip = Column(String, default='')
    expired_time = Column(DateTime(timezone=True), nullable=True, default=None)
    status = Column(Enum(AdminStaffTokenStatus), index=True)
    created_time = Column(DateTime(timezone=True), server_default=func.now())
    updated_time = Column(DateTime(timezone=True),
                          onupdate=func.now(), server_default=func.now())

    staff = relationship('AdminStaff')
