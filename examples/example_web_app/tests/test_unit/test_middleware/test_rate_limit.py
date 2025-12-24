"""
Unit tests for rate limiting functionality.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from aiohttp import web

from example_web_app.middleware.rate_limit import RateLimiter, rate_limit_middleware


class TestRateLimiter:
    """Tests for the RateLimiter class."""

    @pytest.mark.asyncio
    @patch('example_web_app.middleware.rate_limit.redis_client')
    async def test_allows_request_under_limit(self, mock_redis):
        """Test that requests under the limit are allowed."""
        mock_redis.client = AsyncMock()

        # Mock pipeline
        mock_pipe = AsyncMock()
        mock_pipe.execute = AsyncMock(return_value=[
            None,  # zremrangebyscore
            None,  # zadd
            5,     # zcard - 5 requests (under 100)
            None,  # expire
        ])
        mock_redis.client.pipeline = MagicMock(return_value=mock_pipe)

        # Create mock request
        request = MagicMock(spec=web.Request)
        request.headers = {}
        request.transport = None

        limiter = RateLimiter(requests=100, window=60)
        allowed, info = await limiter.is_allowed(request)

        assert allowed is True
        assert "X-RateLimit-Limit" in info
        assert info["X-RateLimit-Limit"] == "100"
        assert int(info["X-RateLimit-Remaining"]) == 95

    @pytest.mark.asyncio
    @patch('example_web_app.middleware.rate_limit.redis_client')
    async def test_blocks_request_over_limit(self, mock_redis):
        """Test that requests over the limit are blocked."""
        mock_redis.client = AsyncMock()

        # Mock pipeline
        mock_pipe = AsyncMock()
        mock_pipe.execute = AsyncMock(return_value=[
            None,  # zremrangebyscore
            None,  # zadd
            101,   # zcard - 101 requests (over 100)
            None,  # expire
        ])
        mock_redis.client.pipeline = MagicMock(return_value=mock_pipe)

        request = MagicMock(spec=web.Request)
        request.headers = {}
        request.transport = None

        limiter = RateLimiter(requests=100, window=60)
        allowed, info = await limiter.is_allowed(request)

        assert allowed is False
        assert info["X-RateLimit-Remaining"] == "0"

    @pytest.mark.asyncio
    @patch('example_web_app.middleware.rate_limit.redis_client')
    async def test_allows_all_when_redis_unavailable(self, mock_redis):
        """Test that all requests are allowed when Redis is unavailable."""
        mock_redis.client = None

        request = MagicMock(spec=web.Request)
        request.headers = {}

        limiter = RateLimiter(requests=100, window=60)
        allowed, info = await limiter.is_allowed(request)

        assert allowed is True
        assert info == {}

    @pytest.mark.asyncio
    @patch('example_web_app.middleware.rate_limit.redis_client')
    async def test_uses_x_forwarded_for_header(self, mock_redis):
        """Test that X-Forwarded-For header is used for client identification."""
        mock_redis.client = AsyncMock()

        mock_pipe = AsyncMock()
        mock_pipe.execute = AsyncMock(return_value=[None, None, 1, None])
        mock_redis.client.pipeline = MagicMock(return_value=mock_pipe)

        request = MagicMock(spec=web.Request)
        request.headers = {"X-Forwarded-For": "192.168.1.1, 10.0.0.1"}
        request.transport = None

        limiter = RateLimiter(requests=100, window=60)
        allowed, _ = await limiter.is_allowed(request)

        assert allowed is True


class TestRateLimitMiddleware:
    """Tests for rate limit middleware."""

    @pytest.mark.asyncio
    async def test_middleware_excludes_specified_paths(self):
        """Test that specified paths are excluded from rate limiting."""
        middleware = rate_limit_middleware(
            requests=100,
            window=60,
            exclude_paths=["/health", "/metrics"],
        )

        request = MagicMock(spec=web.Request)
        request.path = "/health"

        handler = AsyncMock(return_value=web.Response(text="OK"))

        response = await middleware(request, handler)

        handler.assert_called_once_with(request)
        assert response.text == "OK"

