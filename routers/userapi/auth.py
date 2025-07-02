from fastapi import APIRouter
from pydantic import BaseModel, Field

from routers.response import R
from routers.userapi.schemas.user import UserSchema

router = APIRouter()


class LoginForm(BaseModel):
    username: str = Field(max_length=32, min_length=1, description="用户名")
    password: str = Field(min_length=1, max_length=64, description="密码")


@router.put("/login", response_model=R[UserSchema], summary="用户登录", description="用户登录，使用用户名和密码")
async def login(req_form: LoginForm):
    return R.success(UserSchema(id=1, username=req_form.username))
