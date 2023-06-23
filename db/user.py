from sqlalchemy.orm import Session
from sqlalchemy import update
from db.models import User, UserToken, PasswordType, UserStatus, UserTokenStatus, random_password_type, random_salt, encrypt_password
from datetime import datetime
import random
import string
import hashlib


def get_user_by_phone(db: Session, phone: str):
    '''根据手机号获取用户'''
    return db.query(User).filter(User.phone == phone).first()


def create_user(db: Session, phone: str, password: str, nickname: str = '', avatar: str = ''):
    '''创建用户'''
    with db.begin_nested() as tx:
        user = get_user_by_phone(db, phone)
        if user:
            return user

        ptype = random_password_type()
        salt = ''.join(random.choice(string.ascii_letters) for i in range(10))
        user = User(
            phone=phone,
            salt=salt,
            ptype=ptype,
            password=encrypt_password(ptype, salt, password) if password else '',
            nickname=nickname,
            avatar=avatar,
            status=UserStatus.OK,
        )
        db.add(user)
        tx.commit()
        return user


def create_user_token(db: Session, user_id: int, ip: str, device: str, expired_time: datetime | None = None, method: str = ''):
    with db.begin_nested() as tx:
        db.execute(update(UserToken).where(UserToken.user_id == user_id,
                   UserToken.status == UserTokenStatus.OK).values(status=UserTokenStatus.Invalid))
        token = UserToken(
            user_id=user_id,
            ip=ip,
            device=device,
            expired_time=expired_time,
            method=method,
            status=UserTokenStatus.OK,
        )
        db.add(token)
        tx.commit()
        return token


def get_user_token(db: Session, id: str):
    '''根据手机号获取用户'''
    return db.query(UserToken).filter(UserToken.id == id).first()


def set_user_token_invalid(db: Session, id: str):
    '''将Token设置成无效'''
    with db.begin_nested() as tx:
        db.execute(update(UserToken).where(UserToken.id ==
                   id).values(status=UserTokenStatus.Invalid))
        tx.commit()
