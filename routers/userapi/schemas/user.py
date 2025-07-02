from routers.userapi.schemas.base import BaseSchema


class UserSchema(BaseSchema):
    id: int
    username: str
