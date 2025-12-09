from redis.asyncio import Redis

from app.core.config import Settings


def create_redis(settings: Settings) -> Redis:
    return Redis.from_url(settings.redis.url, encoding='utf-8', decode_responses=True)
