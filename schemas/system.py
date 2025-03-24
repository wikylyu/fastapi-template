from pydantic import BaseModel

from schemas.base import BaseSchema


class Endpoint(BaseModel):
    method: str
    path: str


class ApiSchema(BaseSchema):
    id: int
    method: str
    path: str
    permission_ids: list[int]


class PermissionSchema(BaseSchema):
    id: int
    name: str
    code: str
    parent_id: int
    remark: str
    sort: int

    children: list["PermissionSchema"] = []
