from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select, func, select


class BaseRepo:
    @classmethod
    async def _query_pagination[T](
        cls, db: AsyncSession, query: Select, page: int, page_size: int, fetch_all: bool = False
    ) -> tuple[list[T], int]:
        # 分页查询
        paginated_query = query.limit(page_size).offset((page - 1) * page_size)
        r = await db.execute(paginated_query)
        if fetch_all:
            items = r.fetchall()
        else:
            items = r.scalars().all()

        # 总数查询
        count_query = select(func.count()).select_from(query.subquery())
        r_count = await db.execute(count_query)
        total_count = r_count.scalar()

        return (items, total_count)
