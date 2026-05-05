from collections.abc import AsyncGenerator

from redis.asyncio import Redis

from src.config import settings

_redis: Redis | None = None  # type: ignore[type-arg]


async def get_redis() -> AsyncGenerator[Redis, None]:  # type: ignore[type-arg]
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    yield _redis


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None
