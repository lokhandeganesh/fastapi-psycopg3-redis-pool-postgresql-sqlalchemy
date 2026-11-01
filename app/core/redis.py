import redis.asyncio as aioredis


class RedisManager:
    pool: aioredis.ConnectionPool | None = None

    @classmethod
    def get_pool(cls) -> aioredis.ConnectionPool:
        if cls.pool is None:
            cls.pool = aioredis.ConnectionPool.from_url(
                "redis://localhost:6379/0",
                max_connections=20,
                decode_responses=True,
            )
        return cls.pool


async def get_redis() -> aioredis.Redis:
    pool = RedisManager.get_pool()
    return aioredis.Redis(connection_pool=pool)
