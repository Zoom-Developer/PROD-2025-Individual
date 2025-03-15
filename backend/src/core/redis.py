from redis.asyncio import Redis

from src.config import config


redis_factory = lambda: Redis(
    host=config.redis_host,
    port=config.redis_port
)
