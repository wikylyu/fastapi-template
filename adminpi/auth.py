from fastapi import Depends, Cookie, HTTPException,Request
from sqlalchemy.orm import Session
from typing import Annotated
from db import staff as staffdb
from db.models import AdminStaffTokenStatus, AdminStaff, AdminStaffStatus
from db.psql import get_psql
from datetime import datetime

SessionStaffTokenKey = 'stafftoken'


async def try_current_staff(request:Request, db: Session = Depends(get_psql)):
    '''获取当前登录用户，如果没有用户，则返回None'''
    stafftoken=request.session.get(SessionStaffTokenKey)
    if not stafftoken:
        return None
    token = staffdb.get_admin_staff_token(db, stafftoken)
    if not token or token.status != AdminStaffTokenStatus.OK:
        return None
    elif token.expired_time and datetime.now().timestamp() >= token.expired_time.timestamp():
        return None
    staff = token.staff
    if staff.status != AdminStaffStatus.OK and not staff.is_superuser:
        return None
    staff.current_token = token
    return staff


async def get_current_staff(staff: AdminStaff = Depends(try_current_staff)):
    '''获取当前登录用户，如果没有登录，触发401错误'''
    if not staff:
        raise HTTPException(status_code=401)
    return staff


async def get_super_staff(staff: AdminStaff = Depends(get_current_staff)):
    '''获取超级管理员'''
    if not staff.is_superuser:
        raise HTTPException(status_code=401)
    return staff
