"""
Unit tests for caching functionality.
"""
import json
from unittest.mock import AsyncMock, patch

import pytest

from {{cookiecutter.app_name}}.core.cache import cache, invalidate_cache


class TestCacheDecorator:
    """Tests for the @cache decorator."""

    @pytest.mark.asyncio
    @patch('{{cookiecutter.app_name}}.core.cache.redis_client')
    async def test_cache_miss_calls_function(self, mock_redis):
        """Test that cache miss calls the underlying function."""
        mock_redis.client = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()

        call_count = 0

        @cache(ttl=60)
        async def my_function(x):
            nonlocal call_count
            call_count += 1
            return {"result": x * 2}

        result = await my_function(5)

        assert result == {"result": 10}
        assert call_count == 1
        mock_redis.set.assert_called_once()

    @pytest.mark.asyncio
    @patch('{{cookiecutter.app_name}}.core.cache.redis_client')
    async def test_cache_hit_returns_cached_value(self, mock_redis):
        """Test that cache hit returns cached value without calling function."""
        mock_redis.client = AsyncMock()
        mock_redis.get = AsyncMock(return_value=json.dumps({"result": 10}))

        call_count = 0

        @cache(ttl=60)
        async def my_function(x):
            nonlocal call_count
            call_count += 1
            return {"result": x * 2}

        result = await my_function(5)

        assert result == {"result": 10}
        assert call_count == 0  # Function not called

    @pytest.mark.asyncio
    @patch('{{cookiecutter.app_name}}.core.cache.redis_client')
    async def test_cache_disabled_when_redis_unavailable(self, mock_redis):
        """Test that caching is skipped when Redis is unavailable."""
        mock_redis.client = None

        call_count = 0

        @cache(ttl=60)
        async def my_function(x):
            nonlocal call_count
            call_count += 1
            return {"result": x * 2}

        result = await my_function(5)

        assert result == {"result": 10}
        assert call_count == 1

    @pytest.mark.asyncio
    @patch('{{cookiecutter.app_name}}.core.cache.redis_client')
    async def test_custom_key_builder(self, mock_redis):
        """Test cache with custom key builder."""
        mock_redis.client = AsyncMock()
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock()

        @cache(ttl=60, key_builder=lambda user_id: f"user:{user_id}")
        async def get_user(user_id: int):
            return {"id": user_id, "name": "Test"}

        await get_user(123)

        # Verify the cache key includes our custom prefix
        set_call = mock_redis.set.call_args
        assert "user:123" in set_call[0][0]


class TestInvalidateCache:
    """Tests for cache invalidation."""

    @pytest.mark.asyncio
    @patch('{{cookiecutter.app_name}}.core.cache.redis_client')
    async def test_invalidate_cache_deletes_matching_keys(self, mock_redis):
        """Test that invalidate_cache deletes matching keys."""
        mock_redis.client = AsyncMock()

        # Mock scan_iter to return some keys
        async def mock_scan_iter(match=None):
            for key in ["cache:user:1", "cache:user:2"]:
                yield key

        mock_redis.client.scan_iter = mock_scan_iter
        mock_redis.delete = AsyncMock(return_value=2)

        deleted = await invalidate_cache("cache:user:*")

        assert deleted == 2
        mock_redis.delete.assert_called_once()

    @pytest.mark.asyncio
    @patch('{{cookiecutter.app_name}}.core.cache.redis_client')
    async def test_invalidate_cache_returns_zero_when_no_redis(self, mock_redis):
        """Test invalidate returns 0 when Redis is unavailable."""
        mock_redis.client = None

        deleted = await invalidate_cache("cache:*")

        assert deleted == 0

