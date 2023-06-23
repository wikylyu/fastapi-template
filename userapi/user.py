from fastapi import APIRouter,Depends,Header,Response,Request
from api.response import success_response,failure_response
from api.status import ApiStatus
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from db.psql import get_psql
from db.models import User
from db import user as userdb
from db import schema
from typing import Annotated
from datetime import datetime,timedelta
from userapi.auth import SessionUserTokenKey,get_current_user

router = APIRouter()


class SendLoginCodeRequest(BaseModel):
    phone: str = Field(min_length=1)


@router.put('/login/code')
async def send_login_code(req: SendLoginCodeRequest):
    '''发送登录用的短信验证码'''

    # TODO 添加发送短信的代码
    return success_response(None)


class LoginWithPhoneRequest(BaseModel):

    phone: str = Field(min_length=1)
    code: str = Field(min_length=1)

CookieUserTokenKey="usertoken"

@router.put('/login')
async def login_with_phone(req:LoginWithPhoneRequest,request:Request, user_agent: Annotated[str | None, Header()],
                x_forwarded_for: Annotated[str | None, Header()] = None, db: Session = Depends(get_psql)):
    '''使用手机号登陆'''

    # TODO 检查短信验证码
    if req.code!='123456':
        return failure_response(ApiStatus.UserPasswordIncorrect)

    user = userdb.get_user_by_phone(db,req.phone)
    if not user: # 用户不存在，则创建
        user = userdb.create_user(db,req.phone,'','SEOUSER','')
    
    days=30
    expired_time=datetime.now()+timedelta(days=days)
    token=userdb.create_user_token(db,user.id,x_forwarded_for,user_agent,expired_time=expired_time,method='Phone')
    request.session[SessionUserTokenKey]=str(token.id)

    return success_response(user, schema.User)

@router.put('/logout')
async def logout(request:Request, user:User=Depends(get_current_user), db: Session = Depends(get_psql)):
    '''注销当前登陆'''
    userdb.set_user_token_invalid(db,user.current_token.id)
    request.session[SessionUserTokenKey]=''
    return success_response(None)