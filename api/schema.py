
from datetime import datetime
from pydantic import BaseModel
from db.models import AdminStaffStatus, AdminStaffTokenStatus, UserStatus
import uuid

'''
记录返回给客户端的数据结构
'''


class AdminStaff(BaseModel):
    id: int
    username: str
    name: str
    phone: str
    email: str
    status: AdminStaffStatus
    is_superuser: bool
    created_time: datetime
    updated_time: datetime

    class Config:
        orm_mode = True


class AdminStaffToken(BaseModel):
    id: uuid.UUID
    staff_id: int
    device: str
    ip: str
    expired_time: datetime | None
    status: AdminStaffTokenStatus
    created_time: datetime
    updated_time: datetime

    class Config:
        orm_mode = True


class User(BaseModel):
    id: int
    phone: str
    nickname: str
    avatar: str
    gender: str
    status: UserStatus
    wxopenid: str
    wxunionid: str
    created_time: datetime
    updated_time: datetime

    class Config:
        orm_mode = True
