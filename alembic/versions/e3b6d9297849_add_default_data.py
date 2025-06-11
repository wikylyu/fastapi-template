"""add_default_data

Revision ID: e3b6d9297849
Revises: 916a66f048af
Create Date: 2025-06-11 10:36:47.601688

"""

from typing import Sequence, Union

from sqlalchemy.orm import sessionmaker

from alembic import op
from config import DATABASE_TABLE_PREFIX
from models.system import Api, Permission

# revision identifiers, used by Alembic.
revision: str = "e3b6d9297849"
down_revision: Union[str, None] = "916a66f048af"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    Session = sessionmaker(bind=op.get_bind())
    session = Session()
    permissions = [
        Permission(id=1, name="账号管理", code="admin", parent_id=0, remark="", sort=0, created_by=1, deleted=False),
        Permission(id=2, name="账号列表", code="user", parent_id=1, remark="", sort=0, created_by=1, deleted=False),
        Permission(id=3, name="菜单", code="menu", parent_id=2, remark="", sort=0, created_by=1, deleted=False),
        Permission(id=4, name="创建账号", code="create", parent_id=2, remark="", sort=1, created_by=1, deleted=False),
        Permission(id=5, name="编辑账号", code="update", parent_id=2, remark="", sort=2, created_by=1, deleted=False),
        Permission(id=6, name="角色管理", code="role", parent_id=1, remark="", sort=1, created_by=1, deleted=False),
        Permission(id=7, name="菜单", code="menu", parent_id=6, remark="", sort=0, created_by=1, deleted=False),
        Permission(id=8, name="创建角色", code="create", parent_id=6, remark="", sort=1, created_by=1, deleted=False),
        Permission(id=9, name="编辑角色", code="update", parent_id=6, remark="", sort=2, created_by=1, deleted=False),
    ]
    session.add_all(permissions)
    session.flush()  # 确保 permission 数据提交到数据库，以便 t_api 使用

    # 插入 t_api 表数据
    apis = [
        Api(id=1, method="GET", path="/admin/users", permission_ids=[3, 4, 5], created_by=1, deleted=False),
        Api(id=2, method="GET", path="/admin/role/{id}", permission_ids=[3, 4, 5], created_by=1, deleted=False),
        Api(id=3, method="POST", path="/admin/user", permission_ids=[4], created_by=1, deleted=False),
        Api(id=4, method="PUT", path="/admin/user/{id}", permission_ids=[5], created_by=1, deleted=False),
        Api(id=6, method="GET", path="/system/permissions", permission_ids=[8, 9], created_by=1, deleted=False),
        Api(id=7, method="POST", path="/admin/role", permission_ids=[8], created_by=1, deleted=False),
        Api(id=8, method="PUT", path="/admin/role/{id}", permission_ids=[9], created_by=1, deleted=False),
    ]
    session.add_all(apis)
    session.flush()  # 提交 api 数据

    # 设置自增 ID 位置
    op.execute(
        f"SELECT setval('{DATABASE_TABLE_PREFIX}permission_id_seq', (SELECT MAX(id) FROM {DATABASE_TABLE_PREFIX}permission))"
    )
    op.execute(f"SELECT setval('{DATABASE_TABLE_PREFIX}api_id_seq', (SELECT MAX(id) FROM {DATABASE_TABLE_PREFIX}api))")

    session.commit()


def downgrade() -> None:
    """Downgrade schema."""
    Session = sessionmaker(bind=op.get_bind())
    session = Session()

    # 删除 t_api 表数据
    session.query(Api).filter(Api.id.in_([1, 2, 3, 4, 6, 7, 8])).delete(synchronize_session=False)

    # 删除 t_permission 表数据
    session.query(Permission).filter(Permission.id.in_([1, 2, 3, 4, 5, 6, 7, 8, 9])).delete(synchronize_session=False)

    session.commit()

    # 重置自增 ID 序列
    op.execute(
        f"SELECT setval('{DATABASE_TABLE_PREFIX}permission_id_seq', (SELECT MAX(id) FROM {DATABASE_TABLE_PREFIX}permission))"
    )
    op.execute(f"SELECT setval('{DATABASE_TABLE_PREFIX}api_id_seq', (SELECT MAX(id) FROM {DATABASE_TABLE_PREFIX}api))")
