from redis import asyncio as aioredis

from config import REDIS_URL

redis = aioredis.from_url(REDIS_URL, encoding="utf-8", decode_responses=True)


async def get_redis() -> aioredis.Redis:
    global redis
    return redis
