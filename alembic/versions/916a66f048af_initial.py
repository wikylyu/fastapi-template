"""2025-06-11

Revision ID: 916a66f048af
Revises:
Create Date: 2025-06-11 10:36:14.619627

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op
from config import DATABASE_TABLE_PREFIX

# revision identifiers, used by Alembic.
revision: str = "916a66f048af"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    admin_role_table = f"{DATABASE_TABLE_PREFIX}admin_role"

    op.create_table(
        admin_role_table,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("remark", sa.String(length=256), nullable=False),
        sa.Column("permission_ids", postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        "idx_admin_role__permission_ids_gin",
        admin_role_table,
        ["permission_ids"],
        unique=False,
        schema="public",
        postgresql_using="gin",
    )
    op.create_index(
        op.f("ix_public_admin_role_created_at"), admin_role_table, ["created_at"], unique=False, schema="public"
    )
    op.create_index(
        op.f("ix_public_admin_role_created_by"), admin_role_table, ["created_by"], unique=False, schema="public"
    )
    op.create_index(op.f("ix_public_admin_role_deleted"), admin_role_table, ["deleted"], unique=False, schema="public")

    admin_user_table = f"{DATABASE_TABLE_PREFIX}admin_user"
    op.create_table(
        admin_user_table,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("email", sa.String(length=64), nullable=False),
        sa.Column("phone", sa.String(length=32), nullable=False),
        sa.Column("password", sa.String(length=256), nullable=False),
        sa.Column("salt", sa.String(length=32), nullable=False),
        sa.Column("ptype", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("is_superuser", sa.Boolean(), nullable=False),
        sa.Column("created_by", sa.Integer(), server_default="0", nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
        schema="public",
    )
    op.create_index(
        "idx_name_trgm",
        admin_user_table,
        ["name"],
        unique=False,
        schema="public",
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )
    op.create_index(
        "idx_username_trgm",
        admin_user_table,
        ["username"],
        unique=False,
        schema="public",
        postgresql_using="gin",
        postgresql_ops={"username": "gin_trgm_ops"},
    )
    op.create_index(
        op.f("ix_public_admin_user_created_at"), admin_user_table, ["created_at"], unique=False, schema="public"
    )
    op.create_index(
        op.f("ix_public_admin_user_created_by"), admin_user_table, ["created_by"], unique=False, schema="public"
    )
    op.create_index(op.f("ix_public_admin_user_deleted"), admin_user_table, ["deleted"], unique=False, schema="public")
    op.create_index(op.f("ix_public_admin_user_status"), admin_user_table, ["status"], unique=False, schema="public")

    admin_user_role_table = f"{DATABASE_TABLE_PREFIX}admin_user_role"
    op.create_table(
        admin_user_role_table,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("admin_user_id", sa.Integer(), nullable=False),
        sa.Column("admin_role_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("admin_user_id", "admin_role_id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_admin_user_role_admin_role_id"),
        admin_user_role_table,
        ["admin_role_id"],
        unique=False,
        schema="public",
    )
    op.create_index(
        op.f("ix_public_admin_user_role_admin_user_id"),
        admin_user_role_table,
        ["admin_user_id"],
        unique=False,
        schema="public",
    )
    op.create_index(
        op.f("ix_public_admin_user_role_created_at"),
        admin_user_role_table,
        ["created_at"],
        unique=False,
        schema="public",
    )
    op.create_index(
        op.f("ix_public_admin_user_role_deleted"), admin_user_role_table, ["deleted"], unique=False, schema="public"
    )
    admin_user_token_table = f"{DATABASE_TABLE_PREFIX}admin_user_token"
    op.create_table(
        admin_user_token_table,
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("admin_user_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("expired_at", sa.DateTime(), nullable=True),
        sa.Column("ip", sa.String(length=128), nullable=False),
        sa.Column("user_agent", sa.String(length=512), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="public",
    )
    op.create_index(
        op.f("ix_public_admin_user_token_admin_user_id"),
        admin_user_token_table,
        ["admin_user_id"],
        unique=False,
        schema="public",
    )
    op.create_index(
        op.f("ix_public_admin_user_token_created_at"),
        admin_user_token_table,
        ["created_at"],
        unique=False,
        schema="public",
    )
    op.create_index(
        op.f("ix_public_admin_user_token_deleted"), admin_user_token_table, ["deleted"], unique=False, schema="public"
    )
    op.create_index(
        op.f("ix_public_admin_user_token_status"), admin_user_token_table, ["status"], unique=False, schema="public"
    )

    api_table = f"{DATABASE_TABLE_PREFIX}api"
    op.create_table(
        api_table,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("method", sa.String(length=32), nullable=False),
        sa.Column("path", sa.String(length=256), nullable=False),
        sa.Column("permission_ids", postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("method", "path"),
        schema="public",
    )
    op.create_index(
        "idx_api__permission_ids_gin",
        api_table,
        ["permission_ids"],
        unique=False,
        schema="public",
        postgresql_using="gin",
    )
    op.create_index(op.f("ix_public_api_created_at"), api_table, ["created_at"], unique=False, schema="public")
    op.create_index(op.f("ix_public_api_created_by"), api_table, ["created_by"], unique=False, schema="public")
    op.create_index(op.f("ix_public_api_deleted"), api_table, ["deleted"], unique=False, schema="public")
    op.create_index(op.f("ix_public_api_method"), api_table, ["method"], unique=False, schema="public")
    op.create_index(op.f("ix_public_api_path"), api_table, ["path"], unique=False, schema="public")

    permission_table = f"{DATABASE_TABLE_PREFIX}permission"
    op.create_table(
        permission_table,
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=False),
        sa.Column("remark", sa.String(length=256), nullable=False),
        sa.Column("sort", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("deleted", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("parent_id", "code"),
        schema="public",
    )
    op.create_index(op.f("ix_public_permission_code"), permission_table, ["code"], unique=False, schema="public")
    op.create_index(
        op.f("ix_public_permission_created_at"), permission_table, ["created_at"], unique=False, schema="public"
    )
    op.create_index(
        op.f("ix_public_permission_created_by"), permission_table, ["created_by"], unique=False, schema="public"
    )
    op.create_index(op.f("ix_public_permission_deleted"), permission_table, ["deleted"], unique=False, schema="public")
    op.create_index(
        op.f("ix_public_permission_parent_id"), permission_table, ["parent_id"], unique=False, schema="public"
    )
    op.create_index(op.f("ix_public_permission_sort"), permission_table, ["sort"], unique=False, schema="public")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table(f"{DATABASE_TABLE_PREFIX}permission", schema="public")
    op.drop_table(f"{DATABASE_TABLE_PREFIX}api", schema="public")
    op.drop_table(f"{DATABASE_TABLE_PREFIX}admin_user_token", schema="public")
    op.drop_table(f"{DATABASE_TABLE_PREFIX}admin_user_role", schema="public")
    op.drop_table(f"{DATABASE_TABLE_PREFIX}admin_user", schema="public")
    op.drop_table(f"{DATABASE_TABLE_PREFIX}admin_role", schema="public")
    # ### end Alembic commands ###
