from fastapi import APIRouter, Depends, HTTPException, Request, Response, Header
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db.psql import get_psql
from db.models import AdminStaffStatus, AdminStaff
from db import staff as staffdb
from db import schema
from pydantic import BaseModel, Field
from api.status import AdminpiStatus
from api.response import success_response, failure_response
from datetime import datetime, timedelta
from typing import Annotated
from adminpi.auth import get_current_staff, try_current_staff,SessionStaffTokenKey
from fast_captcha import img_captcha
import re

router = APIRouter()


@router.get('/superuser')
async def get_superuser(db: Session = Depends(get_psql)):
    '''获取当前的超级用户信息'''
    superuser = staffdb.get_superuser(db)
    return success_response(bool(superuser))


class CreateSuperuserRequest(BaseModel):
    username: str = Field(min_length=4)
    name: str = Field(min_length=1)
    password: str = Field(min_length=6)


@router.post('/superuser')
async def create_superuser(req: CreateSuperuserRequest, db: Session = Depends(get_psql)):
    '''创建超级用户，只有在超级用户不存在的时候才能创建'''
    superuser = staffdb.create_superuser(
        db, req.username, req.name, req.password)
    return success_response(bool(superuser))


class LoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)
    captcha: str = Field(min_length=1)
    remember: bool = False


SessionLoginCaptchaKey = 'logincaptcha'


@router.put('/login')
async def login(req: LoginRequest, request: Request, response: Response, user_agent: Annotated[str | None, Header()],
                x_forwarded_for: Annotated[str | None, Header()] = None,
                db: Session = Depends(get_psql)):
    captcha = request.session.get(SessionLoginCaptchaKey) or ''
    request.session[SessionLoginCaptchaKey] = ''
    if not captcha or captcha.lower() != req.captcha.lower():  # 验证码错误
        return failure_response(AdminpiStatus.AdminStaffCaptchaIncorrect)

    staff = staffdb.get_admin_staff_by_username(db, req.username)
    if not staff:
        return failure_response(AdminpiStatus.AdminStaffNotFound)
    if not staff.check_password(req.password):  # 密码错误
        return failure_response(AdminpiStatus.AdminStaffPasswordIncorrect)
    if staff.status != AdminStaffStatus.OK:
        return failure_response(AdminpiStatus.AdminStaffBanned)

    days = 30 if req.remember else 1

    token = staffdb.create_admin_staff_token(
        db, staff.id, x_forwarded_for, user_agent, expired_time=datetime.now()+timedelta(days=days))
    request.session[SessionStaffTokenKey]=str(token.id)

    return success_response(staff, schema.AdminStaff)


@router.get('/login/captcha')
async def get_captch(request: Request):
    img, text = img_captcha(code_num=5,  img_type='png')
    request.session[SessionLoginCaptchaKey] = text
    return StreamingResponse(content=img, media_type='image/png')


@router.put('/logout')
async def logout(request: Request, self: AdminStaff = Depends(get_current_staff), db: Session = Depends(get_psql)):
    '''注销用户'''
    request.session[SessionStaffTokenKey]=''
    staffdb.set_admin_staff_token_invalid(db, self.current_token.id)
    return success_response(None)


@router.get('/self')
async def get_self(self: AdminStaff = Depends(get_current_staff)):
    return success_response(self, schema.AdminStaff)


@router.get('/self/try')
async def get_self(self: AdminStaff = Depends(try_current_staff)):
    return success_response(self, schema.AdminStaff)


class UpdateSelfRequest(BaseModel):

    name: str = Field(min_length=1)
    phone: str = ''
    email: str = ''


@router.put('/self')
async def update_self(req: UpdateSelfRequest, self: AdminStaff = Depends(get_current_staff), db: Session = Depends(get_psql)):
    staffdb.update_admin_staff(db, self.id, req.name, req.phone, req.email)
    self = staffdb.get_admin_staff(db, self.id)
    return success_response(self, schema.AdminStaff)


class UpdateSelfPasswordRequest(BaseModel):

    old: str = Field(min_length=1)
    new: str = Field(min_length=6)


@router.put('/self/password')
async def update_self_password(req: UpdateSelfPasswordRequest, self: AdminStaff = Depends(get_current_staff), db: Session = Depends(get_psql)):
    '''修改账号密码'''
    if not staffdb.check_admin_staff_password(self, req.old):
        return failure_response(AdminpiStatus.AdminStaffPasswordIncorrect)
    # 新密码格式不正确
    if not re.search('^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', req.new):
        return failure_response(AdminpiStatus.AdminStaffPasswordMisformed)

    staffdb.update_admin_staff_password(db, self.id, req.new)
    return success_response(None)
