from fastapi import Request,Depends,HTTPException
from db.psql import get_psql
from sqlalchemy.orm import Session
from db import user as userdb
from db.models import UserTokenStatus,User,UserStatus
from datetime import datetime

SessionUserTokenKey = 'usertoken'


async def try_current_user(request:Request, db: Session = Depends(get_psql)):
    '''获取当前登录用户，如果没有用户，则返回None'''
    usertoken=request.session.get(SessionUserTokenKey)
    if not usertoken:
        return None
    token = userdb.get_user_token(db, usertoken)
    if not token or token.status != UserTokenStatus.OK:
        return None
    elif token.expired_time and datetime.now().timestamp() >= token.expired_time.timestamp():
        return None
    user = token.user
    if user.status != UserStatus.OK:
        return None
    user.current_token = token
    return user


async def get_current_user(user: User = Depends(try_current_user)):
    '''获取当前登录用户，如果没有登录，触发401错误'''
    if not user:
        raise HTTPException(status_code=401)
    return user
