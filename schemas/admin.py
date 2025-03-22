from datetime import datetime

from pydantic import BaseModel

from schemas.base import BaseSchema


class AdminConfigSchema(BaseModel):
    onboarding: bool
    version: str
    appname: str
    copyright: str

    admin_username_pattern: str


class AdminUserSchema(BaseSchema):
    id: int
    username: str
    name: str
    email: str
    phone: str
    status: str
    is_superuser: bool


class AdminUserTokenSchema(BaseSchema):
    id: str
    admin_user_id: int
    status: str
    expired_at: datetime
    ip: str
    user_agent: str
