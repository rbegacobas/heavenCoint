"""Redis connection manager."""

import redis.asyncio as redis

from app.core.config import settings

redis_client = redis.from_url(
    settings.redis_url,
    decode_responses=True,
)


async def get_redis() -> redis.Redis:  # type: ignore[type-arg]
    """Return the shared Redis client."""
    return redis_client
