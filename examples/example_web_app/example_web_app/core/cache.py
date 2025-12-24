"""
Caching utilities using Redis.

Provides a simple decorator for caching function results.
"""
import functools
import hashlib
import json
from collections.abc import Callable
from typing import Any, ParamSpec, TypeVar

from example_web_app.core.logger import get_logger
from example_web_app.core.redis import redis_client

__all__ = [
    "cache",
    "invalidate_cache",
]

_logger = get_logger()

P = ParamSpec("P")
R = TypeVar("R")


def _make_cache_key(prefix: str, func: Callable, args: tuple, kwargs: dict) -> str:
    """Generate a cache key from function arguments."""
    key_parts = [prefix, func.__module__, func.__name__]

    # Add args and kwargs to key
    for arg in args:
        if hasattr(arg, "__dict__"):
            # Skip request objects and similar
            continue
        key_parts.append(str(arg))

    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}={v}")

    key_string = ":".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache(
    ttl: int = 60,
    prefix: str = "cache",
    key_builder: Callable[..., str] | None = None,
):
    """
    Decorator to cache function results in Redis.

    Args:
        ttl: Time-to-live in seconds (default: 60)
        prefix: Cache key prefix (default: "cache")
        key_builder: Optional custom function to build cache keys

    Usage:
        @cache(ttl=300)
        async def get_expensive_data(user_id: int):
            ...

        @cache(ttl=60, key_builder=lambda user_id: f"user:{user_id}")
        async def get_user(user_id: int):
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Skip caching if Redis is not available
            if redis_client.client is None:
                return await func(*args, **kwargs)

            # Build cache key
            if key_builder:
                cache_key = f"{prefix}:{key_builder(*args, **kwargs)}"
            else:
                cache_key = f"{prefix}:{_make_cache_key(prefix, func, args, kwargs)}"

            # Try to get from cache
            try:
                cached = await redis_client.get(cache_key)
                if cached is not None:
                    _logger.debug("cache_hit", key=cache_key)
                    return json.loads(cached)
            except Exception as e:
                _logger.warning("cache_get_error", key=cache_key, error=str(e))

            # Call function and cache result
            result = await func(*args, **kwargs)

            try:
                await redis_client.set(cache_key, json.dumps(result), ex=ttl)
                _logger.debug("cache_set", key=cache_key, ttl=ttl)
            except Exception as e:
                _logger.warning("cache_set_error", key=cache_key, error=str(e))

            return result

        return wrapper

    return decorator


async def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache entries matching a pattern.

    Args:
        pattern: Redis key pattern (e.g., "cache:user:*")

    Returns:
        Number of keys deleted
    """
    if redis_client.client is None:
        return 0

    try:
        keys = []
        async for key in redis_client.client.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            deleted = await redis_client.delete(*keys)
            _logger.info("cache_invalidated", pattern=pattern, count=deleted)
            return deleted
        return 0
    except Exception as e:
        _logger.warning("cache_invalidate_error", pattern=pattern, error=str(e))
        return 0

