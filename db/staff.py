from sqlalchemy.orm import Session
from db.models import AdminStaff, PasswordType, AdminStaffToken, AdminStaffStatus, AdminStaffTokenStatus, random_password_type, encrypt_password, random_salt
import random
import string
import hashlib
from datetime import datetime
from sqlalchemy import update, or_


def get_superuser(db: Session):
    '''根据手机号获取用户'''
    return db.query(AdminStaff).filter(AdminStaff.is_superuser == True).first()


def get_admin_staff(db: Session, id: int) -> AdminStaff:
    '''根据ID获取管理员账号'''
    return db.query(AdminStaff).filter(AdminStaff.id == id).first()


def get_admin_staff_by_username(db: Session, username: str) -> AdminStaff:
    '''根据用户名获取管理院长好信息'''
    return db.query(AdminStaff).filter(AdminStaff.username == username).first()


def create_superuser(db: Session, username: str, name: str, plain: str) -> AdminStaff:
    '''创建超级用户，如果已经存在，则返回已存在的超级用户'''
    with db.begin_nested() as tx:
        superuser = db.query(AdminStaff).filter(
            AdminStaff.is_superuser == True).first()
        if superuser:
            return superuser

        ptype = random_password_type()
        salt = random_salt()
        password = encrypt_password(ptype, salt, plain)
        superuser = AdminStaff(
            username=username,
            name=name,
            ptype=ptype,
            salt=salt,
            password=password,
            is_superuser=True,
            created_by=0,
        )
        db.add(superuser)
        tx.commit()
        return superuser


def get_admin_staff_token(db: Session, id: str):
    '''根据手机号获取用户'''
    return db.query(AdminStaffToken).filter(AdminStaffToken.id == id).first()


def create_admin_staff_token(db: Session, staff_id: int, ip: str, device: str, expired_time: datetime | None = None,):
    with db.begin_nested() as tx:
        db.execute(update(AdminStaffToken).where(AdminStaffToken.staff_id == staff_id,
                   AdminStaffToken.status == AdminStaffTokenStatus.OK).values(status=AdminStaffTokenStatus.Invalid))
        token = AdminStaffToken(
            staff_id=staff_id,
            ip=ip,
            device=device,
            expired_time=expired_time,
            status=AdminStaffTokenStatus.OK,
        )
        db.add(token)
        tx.commit()
        return token


def set_admin_staff_token_invalid(db: Session, id: str):
    '''将Token设置成无效'''
    with db.begin_nested() as tx:
        db.execute(update(AdminStaffToken).where(AdminStaffToken.id ==
                   id).values(status=AdminStaffTokenStatus.Invalid))
        tx.commit()


def clear_admin_staff_token(db: Session, staff_id: int):
    '''将该管理员账号的所有登录都强制注销'''
    with db.begin_nested() as tx:
        db.execute(update(AdminStaffToken).where(AdminStaffToken.staff_id ==
                   staff_id).values(status=AdminStaffTokenStatus.Invalid))
        tx.commit()


def update_admin_staff(db: Session, staff_id: int, name: str, phone: str, email: str, status: AdminStaffStatus | None = None):
    '''修改管理员的基本信息'''
    with db.begin_nested() as tx:
        q = update(AdminStaff).where(AdminStaff.id == staff_id).values(
            name=name, phone=phone, email=email)
        if status:
            q = q.values(status=status)
        db.execute(q)
        tx.commit()


def update_admin_staff_password(db: Session, staff_id: int, plain: str):
    '''修改管理账号的密码'''
    with db.begin_nested() as tx:
        ptype = random_password_type()
        salt = random_salt()
        password = encrypt_password(ptype, salt, plain)
        db.execute(update(AdminStaff).where(AdminStaff.id == staff_id).values(
            salt=salt, ptype=ptype, password=password))
        tx.commit()


def find_admin_staffs(db: Session, query: str = '', status: AdminStaffStatus | str = '', page: int = 1, page_size: int = 10):
    q = db.query(AdminStaff)
    if query:
        qry = '%{}%'.format(query)
        q = q.filter(or_(AdminStaff.username.ilike(qry),
                     AdminStaff.phone.ilike(qry), AdminStaff.name.ilike(qry)))
    if status:
        q = q.filter(AdminStaff.status == status)

    total = q.count()

    return q.order_by(AdminStaff.id.desc()).limit(page_size).offset((page-1)*page_size).all(), total


def find_admin_staff_tokens(db: Session, staff_id: int = 0, status: AdminStaffTokenStatus | str = '', page: int = 1, page_size: int = 10):
    q = db.query(AdminStaffToken)
    if staff_id:
        q = q.filter(AdminStaffToken.staff_id == staff_id)
    if status:
        q = q.filter(AdminStaffToken.status == status)

    total = q.count()

    return q.order_by(AdminStaffToken.created_time.desc()).limit(page_size).offset((page-1)*page_size).all(), total
