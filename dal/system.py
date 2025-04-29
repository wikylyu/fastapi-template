from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from dal.base import BaseRepo
from models.system import Api, Permission


class SystemRepo(BaseRepo):
    @classmethod
    async def create_api(
        cls, db: AsyncSession, method: str, path: str, created_by: int = 0, permission_ids: list[int] = []
    ):
        api = Api(method=method, path=path, permission_ids=permission_ids, created_by=created_by)
        db.add(api)
        await db.flush()
        return api

    @classmethod
    async def get_api_by_method_and_path(cls, db: AsyncSession, method: str, path: str):
        r = await db.execute(
            select(Api).where(
                Api.method == method,
                Api.path == path,
            )
        )
        return r.scalars().first()

    @classmethod
    async def get_api(cls, db: AsyncSession, id: int):
        r = await db.execute(select(Api).where(Api.id == id))
        return r.scalars().first()

    @classmethod
    async def delete_api(cls, db: AsyncSession, id: int):
        api = await cls.get_api(db, id)
        if not api:
            return None
        await db.delete(api)
        await db.flush()

    @classmethod
    async def find_apis(
        cls, db: AsyncSession, method: str, path: str, page: int = 1, page_size: int = 10
    ) -> tuple[list[Api], int]:
        q = select(Api).order_by(Api.created_at.desc())
        if method:
            q = q.where(Api.method == method)
        if path:
            q = q.where(Api.path == path)

        return cls._query_pagination(db, q, page, page_size)

    @classmethod
    async def get_permission(cls, db: AsyncSession, id: int, with_for_update: bool = False) -> Permission | None:
        query = select(Permission).where(Permission.id == id)
        if with_for_update:
            query = query.with_for_update()
        r = await db.execute(query)
        return r.scalars().first()

    @classmethod
    async def get_permission_by_fullcode(cls, db: AsyncSession, code: str) -> Permission | None:
        codes = code.split(".")
        parent_id = 0
        permission = None
        for code in codes:
            permission = await cls.get_permission_by_code_and_parent(db, code, parent_id)
            if not permission:
                return None
            parent_id = permission.id
        return permission

    @classmethod
    async def get_permission_by_code_and_parent(cls, db: AsyncSession, code: str, parent_id: int) -> Permission | None:
        r = await db.execute(select(Permission).where(Permission.code == code, Permission.parent_id == parent_id))
        return r.scalars().first()

    @classmethod
    async def find_chilren_permissions_by_parent(cls, db: AsyncSession, parent_id: int) -> list[Permission]:
        r = await db.execute(
            select(Permission).order_by(Permission.sort.asc()).where(Permission.parent_id == parent_id)
        )
        return r.scalars().all()

    @classmethod
    async def find_chilren_permissions_by_parent_r(cls, db: AsyncSession, parent_id: int) -> list[Permission]:
        """递归获取子权限"""
        children = await cls.find_chilren_permissions_by_parent(db, parent_id)
        for child in children:
            child.children = await cls.find_chilren_permissions_by_parent_r(db, child.id)
        return children

    @classmethod
    async def create_permission(
        cls,
        db: AsyncSession,
        name: str,
        code: str,
        remark: str,
        parent_id: int = 0,
        created_by: int = 0,
    ) -> Permission:
        r = await db.execute(
            select(Permission).order_by(Permission.sort.desc()).where(Permission.parent_id == parent_id)
        )
        last = r.scalars().first()
        sort = 0
        if last:
            sort = last.sort + 1

        permission = Permission(
            name=name, code=code, remark=remark, parent_id=parent_id, sort=sort, created_by=created_by
        )
        db.add(permission)
        await db.flush()
        return permission

    @classmethod
    async def delete_permission(cls, db: AsyncSession, id: int):
        permission = await cls.get_permission(db, id, with_for_update=True)
        if not permission:
            return
        children = await cls.find_chilren_permissions_by_parent(db, id)
        for child in children:
            await cls.delete_permission(db, child.id)

        await db.delete(permission)

        await db.execute(
            update(Api)
            .where(Api.permission_ids.contains([id]))
            .values(permission_ids=func.array_remove(Api.permission_ids, id))
        )

    @classmethod
    async def update_permission_sort(cls, db: AsyncSession, id: int, sort: int) -> Permission | None:
        permission = await cls.get_permission(db, id, with_for_update=True)
        if not permission:
            return
        if sort > permission.sort:
            await db.execute(
                update(Permission)
                .where(Permission.sort > permission.sort)
                .where(Permission.sort <= sort)
                .where(Permission.parent_id == permission.parent_id)
                .values(sort=Permission.sort - 1)
            )
        elif sort < permission.sort:
            await db.execute(
                update(Permission)
                .where(Permission.sort >= sort)
                .where(Permission.sort < permission.sort)
                .where(Permission.parent_id == permission.parent_id)
                .values(sort=Permission.sort + 1)
            )
        permission.sort = sort
        await db.flush()
        return permission
