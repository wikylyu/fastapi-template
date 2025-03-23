from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.system import Api


class SystemRepo:
    @classmethod
    async def create_api(cls, db: AsyncSession, method: str, path: str, created_by: int = 0):
        api = Api(method=method, path=path, created_by=created_by)
        db.add(api)
        await db.flush()
        return api

    @classmethod
    async def get_api(cls, db: AsyncSession, method: str, path: str):
        r = await db.execute(select(Api).where(Api.method == method, Api.path == path))
        return r.scalars().first()
