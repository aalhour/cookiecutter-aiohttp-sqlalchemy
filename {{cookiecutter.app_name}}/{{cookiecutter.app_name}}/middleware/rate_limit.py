"""
Rate limiting middleware and decorators using Redis.

Implements a sliding window rate limiter.
"""
import time
from collections.abc import Callable
from typing import Any

from aiohttp import web

from {{cookiecutter.app_name}}.core.logger import get_logger
from {{cookiecutter.app_name}}.core.redis import redis_client

__all__ = [
    "rate_limit_middleware",
    "RateLimiter",
]

_logger = get_logger()


class RateLimiter:
    """
    Sliding window rate limiter using Redis.
    """

    def __init__(
        self,
        requests: int = 100,
        window: int = 60,
        key_prefix: str = "ratelimit",
    ):
        """
        Initialize rate limiter.

        Args:
            requests: Maximum requests allowed in the window
            window: Time window in seconds
            key_prefix: Redis key prefix
        """
        self.requests = requests
        self.window = window
        self.key_prefix = key_prefix

    def _get_client_key(self, request: web.Request) -> str:
        """Get a unique key for the client."""
        # Use X-Forwarded-For if behind proxy, otherwise peer IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            peername = request.transport.get_extra_info("peername") if request.transport else None
            client_ip = peername[0] if peername else "unknown"

        return f"{self.key_prefix}:{client_ip}"

    async def is_allowed(self, request: web.Request) -> tuple[bool, dict[str, Any]]:
        """
        Check if request is allowed under rate limit.

        Returns:
            Tuple of (allowed: bool, info: dict with rate limit headers)
        """
        if redis_client.client is None:
            # No Redis = no rate limiting
            return True, {}

        key = self._get_client_key(request)
        now = time.time()
        window_start = now - self.window

        try:
            pipe = redis_client.client.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Add current request
            pipe.zadd(key, {str(now): now})

            # Count requests in window
            pipe.zcard(key)

            # Set expiration
            pipe.expire(key, self.window)

            results = await pipe.execute()
            request_count = results[2]

            # Calculate remaining and reset time
            remaining = max(0, self.requests - request_count)
            reset_at = int(now + self.window)

            info = {
                "X-RateLimit-Limit": str(self.requests),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(reset_at),
            }

            allowed = request_count <= self.requests

            if not allowed:
                _logger.warning(
                    "rate_limit_exceeded",
                    key=key,
                    count=request_count,
                    limit=self.requests,
                )

            return allowed, info

        except Exception as e:
            _logger.warning("rate_limit_error", error=str(e))
            return True, {}  # Fail open


def rate_limit_middleware(
    requests: int = 100,
    window: int = 60,
    exclude_paths: list[str] | None = None,
):
    """
    Create a rate limiting middleware.

    Args:
        requests: Maximum requests per window
        window: Time window in seconds
        exclude_paths: List of paths to exclude from rate limiting

    Usage:
        app = web.Application(
            middlewares=[
                rate_limit_middleware(requests=100, window=60),
            ]
        )
    """
    limiter = RateLimiter(requests=requests, window=window)
    exclude = set(exclude_paths or [])

    @web.middleware
    async def middleware(request: web.Request, handler: Callable) -> web.Response:
        # Skip rate limiting for excluded paths
        if request.path in exclude:
            return await handler(request)

        allowed, info = await limiter.is_allowed(request)

        if not allowed:
            response = web.json_response(
                {"error": "rate_limit_exceeded", "message": "Too many requests"},
                status=429,
            )
            for key, value in info.items():
                response.headers[key] = value
            return response

        response = await handler(request)

        # Add rate limit headers to response
        for key, value in info.items():
            response.headers[key] = value

        return response

    return middleware

