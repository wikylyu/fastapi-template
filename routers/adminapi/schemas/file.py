from pydantic import Field

from routers.adminapi.schemas.base import BaseSchema


class FileSchema(BaseSchema):
    id: str
    content_type: str
    size: int
    filename: str
    admin_user_id: int = Field(default=0)
