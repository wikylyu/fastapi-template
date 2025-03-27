from sqlalchemy import Column, Index, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import UniqueConstraint

from models.base import BaseTable


class Permission(BaseTable):
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)  # 权限名
    code = Column(String(64), nullable=False, index=True)
    parent_id = Column(Integer, nullable=False, index=True)
    remark = Column(String(256), nullable=False)
    sort = Column(Integer, nullable=False, default=0, index=True)  # 排序
    created_by = Column(Integer, nullable=False, index=True)  # 创建人

    children = []

    __table_args__ = (  # 设置method和path的联合unique
        UniqueConstraint("parent_id", "code", name="parent_code_unique"),
    )


class Api(BaseTable):
    id = Column(Integer, primary_key=True, autoincrement=True)
    method = Column(String(32), nullable=False, index=True)
    path = Column(String(256), nullable=False, index=True)
    permission_ids = Column(ARRAY(Integer), nullable=False, default=[])
    created_by = Column(Integer, nullable=False, index=True)

    __table_args__ = (  # 设置method和path的联合unique
        UniqueConstraint("method", "path", name="api__method_path_unique"),
        Index("idx_api__permission_ids_gin", "permission_ids", postgresql_using="gin"),
    )
