"""
Redis client module for caching, rate limiting, and pub/sub.

Provides async Redis connection management with connection pooling.
"""
import os
from contextlib import asynccontextmanager
from typing import Any

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from example_web_app.core.config import get_settings
from example_web_app.core.logger import get_logger

__all__ = [
    "RedisManager",
    "redis_client",
    "get_redis",
]

_logger = get_logger()


class RedisManager:
    """
    Redis connection manager with connection pooling.
    """

    def __init__(self):
        self._pool: ConnectionPool | None = None
        self._client: Redis | None = None

    @property
    def client(self) -> Redis | None:
        """Get the Redis client instance."""
        return self._client

    def get_redis_url(self) -> str:
        """Build Redis URL from configuration."""
        settings = get_settings()
        host = settings.redis.host
        port = settings.redis.port
        db = settings.redis.db
        password = os.environ.get("REDIS_PASSWORD", settings.redis.password)

        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        return f"redis://{host}:{port}/{db}"

    async def initialize(self, url: str | None = None) -> None:
        """
        Initialize the Redis connection pool.

        Args:
            url: Optional Redis URL. If not provided, builds from config.
        """
        if url is None:
            url = self.get_redis_url()

        settings = get_settings()

        self._pool = ConnectionPool.from_url(
            url,
            max_connections=settings.redis.max_connections,
            decode_responses=True,
        )
        self._client = Redis(connection_pool=self._pool)

        # Test connection
        try:
            await self._client.ping()
            _logger.info("redis_connected", url=url.split("@")[-1])
        except redis.ConnectionError as e:
            _logger.warning("redis_connection_failed", error=str(e))
            self._client = None

    async def cleanup(self) -> None:
        """Close Redis connections."""
        if self._client:
            await self._client.aclose()
            _logger.info("redis_disconnected")

    async def get(self, key: str) -> str | None:
        """Get a value from Redis."""
        if not self._client:
            return None
        return await self._client.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ex: int | None = None,
        px: int | None = None,
    ) -> bool:
        """
        Set a value in Redis.

        Args:
            key: The key to set
            value: The value to store
            ex: Expiration in seconds
            px: Expiration in milliseconds
        """
        if not self._client:
            return False
        await self._client.set(key, value, ex=ex, px=px)
        return True

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys."""
        if not self._client:
            return 0
        return await self._client.delete(*keys)

    async def exists(self, *keys: str) -> int:
        """Check if keys exist."""
        if not self._client:
            return 0
        return await self._client.exists(*keys)

    async def incr(self, key: str, amount: int = 1) -> int | None:
        """Increment a key's value."""
        if not self._client:
            return None
        return await self._client.incrby(key, amount)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on a key."""
        if not self._client:
            return False
        return await self._client.expire(key, seconds)

    async def ttl(self, key: str) -> int:
        """Get time-to-live for a key."""
        if not self._client:
            return -2
        return await self._client.ttl(key)


# Global Redis manager instance
redis_client = RedisManager()


@asynccontextmanager
async def get_redis():
    """
    Async context manager for Redis operations.

    Usage:
        async with get_redis() as r:
            await r.set("key", "value")
    """
    yield redis_client

