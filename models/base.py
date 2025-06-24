import re
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, func
from sqlalchemy.ext.declarative import declared_attr

from config import DATABASE_TABLE_PREFIX
from database.session import Base


def camel_to_snake(name: str) -> str:
    """将驼峰命名法转换为下划线命名法"""
    s1 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", name)
    return s1.lower()


class BaseTable(Base):
    @declared_attr
    def __tablename__(cls):
        return DATABASE_TABLE_PREFIX + camel_to_snake(cls.__name__)

    __abstract__ = True  # 定义为抽象基类
    __allow_unmapped__ = True
    created_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=datetime.now)
    deleted = Column(Boolean, default=False, index=True)

    class Config:
        from_attributes = True
