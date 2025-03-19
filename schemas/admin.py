from pydantic import BaseModel

from schemas.base import BaseSchema


class AdminConfigSchema(BaseModel):
    onboarding: bool
    version: str
    name: str

    admin_username_pattern: str


class AdminUserSchema(BaseSchema):
    id: int
    username: str
    name: str
    status: str
    is_superuser: bool
