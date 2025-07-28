from sqlalchemy import func, select, update

from dal.base import BaseRepo
from models.system import Api, Permission


class SystemRepo(BaseRepo):
    async def create_api(self, method: str, path: str, created_by: int = 0, permission_ids: list[int] = []):
        api = Api(method=method, path=path, permission_ids=permission_ids, created_by=created_by)
        self.db.add(api)
        await self.db.flush()
        return api

    async def get_api_by_method_and_path(self, method: str, path: str):
        r = await self.db.execute(
            select(Api).where(
                Api.method == method,
                Api.path == path,
            )
        )
        return r.scalars().first()

    async def get_api(self, id: int, with_for_update: bool = False) -> Api | None:
        q = select(Api).where(Api.id == id)
        if with_for_update:
            q = q.with_for_update()
        r = await self.db.execute(q)
        return r.scalars().first()

    async def delete_api(self, id: int):
        api = await self.get_api(id)
        if not api:
            return None
        await self.db.delete(api)
        await self.db.flush()

    async def find_apis(self, method: str, path: str, page: int = 1, page_size: int = 10) -> tuple[list[Api], int]:
        q = select(Api).order_by(Api.created_at.desc())
        if method:
            q = q.where(Api.method == method)
        if path:
            q = q.where(Api.path == path)

        return await self._query_pagination(q, page, page_size)

    async def get_permission(self, id: int, with_for_update: bool = False) -> Permission | None:
        query = select(Permission).where(Permission.id == id)
        if with_for_update:
            query = query.with_for_update()
        r = await self.db.execute(query)
        return r.scalars().first()

    async def get_permission_by_fullcode(self, code: str) -> Permission | None:
        codes = code.split(".")
        parent_id = 0
        permission = None
        for code in codes:
            permission = await self.get_permission_by_code_and_parent(code, parent_id)
            if not permission:
                return None
            parent_id = permission.id
        return permission

    async def get_permission_by_code_and_parent(self, code: str, parent_id: int) -> Permission | None:
        q = select(Permission).where(Permission.code == code, Permission.parent_id == parent_id)
        r = await self.db.execute(q)
        return r.scalars().first()

    async def find_chilren_permissions_by_parent(self, parent_id: int) -> list[Permission]:
        r = await self.db.execute(
            select(Permission).order_by(Permission.sort.asc()).where(Permission.parent_id == parent_id)
        )
        return r.scalars().all()

    async def find_chilren_permissions_by_parent_r(self, parent_id: int) -> list[Permission]:
        """递归获取子权限"""
        children = await self.find_chilren_permissions_by_parent(parent_id)
        for child in children:
            child.children = await self.find_chilren_permissions_by_parent_r(child.id)
        return children

    async def create_permission(
        self,
        name: str,
        code: str,
        remark: str,
        parent_id: int = 0,
        created_by: int = 0,
    ) -> Permission:
        r = await self.db.execute(
            select(Permission).order_by(Permission.sort.desc()).where(Permission.parent_id == parent_id)
        )
        last = r.scalars().first()
        sort = 0
        if last:
            sort = last.sort + 1

        permission = Permission(
            name=name, code=code, remark=remark, parent_id=parent_id, sort=sort, created_by=created_by
        )
        self.db.add(permission)
        await self.db.flush()
        return permission

    async def delete_permission(self, id: int):
        permission = await self.get_permission(id, with_for_update=True)
        if not permission:
            return
        children = await self.find_chilren_permissions_by_parent(id)
        for child in children:
            await self.delete_permission(child.id)

        await self.db.delete(permission)

        await self.db.execute(
            update(Api)
            .where(Api.permission_ids.contains([id]))
            .values(permission_ids=func.array_remove(Api.permission_ids, id))
        )

    async def update_permission_sort(self, id: int, sort: int) -> Permission | None:
        permission = await self.get_permission(id, with_for_update=True)
        if not permission:
            return
        if sort > permission.sort:
            await self.db.execute(
                update(Permission)
                .where(Permission.sort > permission.sort)
                .where(Permission.sort <= sort)
                .where(Permission.parent_id == permission.parent_id)
                .values(sort=Permission.sort - 1)
            )
        elif sort < permission.sort:
            await self.db.execute(
                update(Permission)
                .where(Permission.sort >= sort)
                .where(Permission.sort < permission.sort)
                .where(Permission.parent_id == permission.parent_id)
                .values(sort=Permission.sort + 1)
            )
        permission.sort = sort
        await self.db.flush()
        return permission
