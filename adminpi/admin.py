from fastapi import APIRouter, Depends, HTTPException, Request, Response, Header, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from db.psql import get_psql
from db.models import AdminStaffStatus, AdminStaff, AdminStaffTokenStatus
from db import staff as staffdb
from db import schema
from pydantic import BaseModel, Field
from api.status import AdminpiStatus
from api.response import success_response, failure_response
from datetime import datetime, timedelta
from typing import Annotated
from adminpi.auth import get_current_staff, get_super_staff
import re

router = APIRouter()


@router.get('/staffs')
async def find_admin_staffs(query: str = '', status: AdminStaffStatus | str = '',
                            page: Annotated[int, Query(min=1)] = 1, page_size:  Annotated[int, Query(min=1, max=100)] = 10,
                            self: AdminStaff = Depends(get_current_staff), db: Session = Depends(get_psql)):
    '''获取管理员账号列表'''
    staffs, total = staffdb.find_admin_staffs(
        db, query, status, page, page_size)
    return success_response(staffs, schema.AdminStaff, page=page, page_size=page_size, total=total)


@router.get('/staff/tokens')
async def find_admin_staff_tokens(staff_id: int = 0, status: AdminStaffTokenStatus | str = '',
                                  page: Annotated[int, Query(min=1)] = 1, page_size: Annotated[int, Query(min=5, max=100)] = 10,
                                  self: AdminStaff = Depends(get_super_staff), db: Session = Depends(get_psql)):
    '''查询登录记录'''
    tokens, total = staffdb.find_admin_staff_tokens(
        db, staff_id, status, page, page_size)
    return success_response(tokens, schema.AdminStaffToken, page=page, page_size=page_size, total=total)


@router.get('/staff/{id}')
async def get_admin_staff(id: int, self: AdminStaff = Depends(get_current_staff), db: Session = Depends(get_psql)):
    '''获取管理员账号的信息'''
    staff = staffdb.get_admin_staff(db, id)
    return success_response(staff, schema.AdminStaff)


class UpdateAdminStaffRequest(BaseModel):
    name: str = Field(min_length=1)
    phone: str = ''
    email: str = ''
    status: AdminStaffStatus


@router.put('/staff/{id}')
async def update_admin_staff(id: int, req: UpdateAdminStaffRequest, self: AdminStaff = Depends(get_super_staff), db: Session = Depends(get_psql)):
    '''更新管理员账号的基本信息'''

    staffdb.update_admin_staff(
        db, id, req.name, req.phone, req.email, req.status,)
    staff = staffdb.get_admin_staff(db, id)
    return success_response(staff, schema.AdminStaff)


class UpdateAdminStaffPasswordRequest(BaseModel):

    password: str = Field(min_length=6)
    logout: bool = False


@router.put('/staff/{id}/password')
async def update_admin_staff_password(id: int, req: UpdateAdminStaffPasswordRequest, self: AdminStaff = Depends(get_super_staff), db: Session = Depends(get_psql)):
    '''修改管理员账号的密码'''
    if not re.search('^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{6,}$', req.password):
        return failure_response(AdminpiStatus.AdminStaffPasswordMisformed)

    staffdb.update_admin_staff_password(db, id, req.password)
    if req.logout:
        # 将用户强制注销
        staffdb.clear_admin_staff_token(db, id)
    return success_response(None)
