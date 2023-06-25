from fastapi import APIRouter, Depends, HTTPException, Request, Response, Query
from sqlalchemy.orm import Session
from db.psql import get_psql
from db.models import AdminStaffStatus, AdminStaff, UserStatus
from db import user as userdb
from db import schema
from pydantic import BaseModel, Field
from api.status import AdminpiStatus
from api.response import success_response, failure_response
from typing import Annotated
from adminpi.auth import get_current_staff
import re

router = APIRouter()


@router.get('/users')
async def find_users(query: str = '', status: UserStatus | str = '',
                     page: Annotated[int, Query(min=1)] = 1,
                     page_size: Annotated[int, Query(min=5, max=100)] = 10,
                     self: AdminStaff = Depends(get_current_staff), db: Session = Depends(get_psql)):
    users, total = userdb.find_users(db, query, status, page, page_size)
    return success_response(users, schema.User, page, page_size, total)
