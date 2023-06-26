from fastapi import APIRouter, Depends, Header, Response, Request
from api.response import success_response, failure_response, StatusResponse
from api.status import ApiStatus
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from db.psql import get_psql
from db.models import User, UserStatus
from db import user as userdb
from api import schema
from typing import Annotated, Any
from datetime import datetime, timedelta
from userapi.auth import SessionUserTokenKey, get_current_user, try_current_user
from utils.string import random_digit
from service import redis, sms


router = APIRouter()


class SendLoginCodeRequest(BaseModel):
    phone: str = Field(min_length=1)


class SendWait(BaseModel):
    wait: int


@router.put('/login/code', response_model=StatusResponse[SendWait])
async def send_login_code(req: SendLoginCodeRequest):
    '''发送登录用的短信验证码'''
    max_age = 5*60  # 五分钟有效期
    freq_duration = 60  # 60秒发送一次
    key = 'user.login.phone.{}'.format(req.phone)
    ttl = redis.ttl(key)
    if ttl > 0:
        delta = max_age-ttl
        wait = int(freq_duration-delta)
        if wait > 0:  # 发送过快
            return failure_response(ApiStatus.PhoneCodeSentTooFast, SendWait(wait=wait))

    code = random_digit(6)
    if not sms.send_sms(req.phone, 'phonecode', [code, "5"]):
        return failure_response(ApiStatus.PhoneCodeSentFailure, SendWait(wait=0))
    redis.setex(key, code, ex=max_age)
    return success_response(SendWait(wait=freq_duration))


class LoginWithPhoneRequest(BaseModel):

    phone: str = Field(min_length=1)
    code: str = Field(min_length=1)


CookieUserTokenKey = "usertoken"


@router.put('/login', response_model=StatusResponse[schema.User])
async def login_with_phone(req: LoginWithPhoneRequest, request: Request, user_agent: Annotated[str | None, Header()],
                           x_forwarded_for: Annotated[str | None, Header()] = None, db: Session = Depends(get_psql)):
    '''使用手机号登陆'''

    key = 'user.login.phone.{}'.format(req.phone)
    v = redis.get(key)
    if not v or v.decode() != req.code:
        return failure_response(ApiStatus.PhoneCodeIncorrect)
    redis.delete(key)

    user = userdb.get_user_by_phone(db, req.phone)
    if not user:  # 用户不存在，则创建
        user = userdb.create_user(db, req.phone, '', 'SEOUSER', '')
    elif user.status != UserStatus.OK:
        return failure_response(ApiStatus.UserBanned)

    days = 30
    expired_time = datetime.now()+timedelta(days=days)
    token = userdb.create_user_token(
        db, user.id, x_forwarded_for, user_agent, expired_time=expired_time, method='Phone')
    request.session[SessionUserTokenKey] = str(token.id)

    return success_response(user, schema.User)


class LoginWithPasswordRequest(BaseModel):

    phone: str = Field(min_length=1)
    password: str = Field(min_length=1)


@router.put('/plogin', response_model=StatusResponse[schema.User])
async def login_with_password(req: LoginWithPasswordRequest, request: Request, user_agent: Annotated[str | None, Header()],
                              x_forwarded_for: Annotated[str | None, Header()] = None, db: Session = Depends(get_psql)):
    '''使用密码登录'''
    user = userdb.get_user_by_phone(db, req.phone)
    if not user:
        return failure_response(ApiStatus.UserPhoneNotFound)
    if user.status != UserStatus.OK:
        return failure_response(ApiStatus.UserBanned)
    elif not user.check_password(req.password):
        return failure_response(ApiStatus.UserPasswordIncorrect)
    days = 30
    expired_time = datetime.now()+timedelta(days=days)
    token = userdb.create_user_token(
        db, user.id, x_forwarded_for, user_agent, expired_time=expired_time, method='Password')
    request.session[SessionUserTokenKey] = str(token.id)

    return success_response(user, schema.User)


@router.put('/logout', response_model=StatusResponse[None])
async def logout(request: Request, self: User = Depends(get_current_user), db: Session = Depends(get_psql)):
    '''注销当前登陆'''
    userdb.set_user_token_invalid(db, self.current_token.id)
    request.session[SessionUserTokenKey] = ''
    return success_response(None)


@router.get('/self', response_model=StatusResponse[schema.User])
async def get_self(self: User = Depends(get_current_user)):
    '''获取当前登录的用户信息'''
    return success_response(self, schema.User)


@router.get('/self/try', response_model=StatusResponse[schema.User])
async def try_self(self: User = Depends(try_current_user)):
    '''尝试获取用户信息，如果失败返回None'''
    return success_response(self, schema.User)
