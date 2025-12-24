"""
Unit tests for background task functionality.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from {{cookiecutter.app_name}}.tasks.jobs import example_task, send_notification


class TestExampleTask:
    """Tests for example_task background job."""

    @pytest.mark.asyncio
    async def test_example_task_returns_result(self):
        """Test that example_task returns expected result."""
        ctx = {}
        result = await example_task(ctx, name="test", data={"key": "value"})

        assert result["name"] == "test"
        assert result["processed"] is True
        assert result["data"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_example_task_with_no_data(self):
        """Test example_task with no data."""
        ctx = {}
        result = await example_task(ctx, name="test")

        assert result["name"] == "test"
        assert result["processed"] is True
        assert result["data"] is None


class TestSendNotification:
    """Tests for send_notification background job."""

    @pytest.mark.asyncio
    async def test_send_notification_returns_success(self):
        """Test that send_notification returns success status."""
        ctx = {}
        result = await send_notification(
            ctx,
            user_id=123,
            message="Hello!",
            channel="email",
        )

        assert result["user_id"] == 123
        assert result["channel"] == "email"
        assert result["status"] == "sent"

    @pytest.mark.asyncio
    async def test_send_notification_default_channel(self):
        """Test send_notification with default channel."""
        ctx = {}
        result = await send_notification(
            ctx,
            user_id=456,
            message="Test message",
        )

        assert result["channel"] == "email"


class TestEnqueue:
    """Tests for task enqueueing."""

    @pytest.mark.asyncio
    @patch('{{cookiecutter.app_name}}.tasks.worker.get_task_pool')
    async def test_enqueue_returns_job_id(self, mock_get_pool):
        """Test that enqueue returns job ID."""
        from {{cookiecutter.app_name}}.tasks import enqueue

        mock_pool = AsyncMock()
        mock_job = MagicMock()
        mock_job.job_id = "job-123"
        mock_pool.enqueue_job = AsyncMock(return_value=mock_job)
        mock_get_pool.return_value = mock_pool

        job_id = await enqueue("example_task", name="test")

        assert job_id == "job-123"
        mock_pool.enqueue_job.assert_called_once()

    @pytest.mark.asyncio
    @patch('{{cookiecutter.app_name}}.tasks.worker.get_task_pool')
    async def test_enqueue_returns_none_when_no_pool(self, mock_get_pool):
        """Test that enqueue returns None when pool not initialized."""
        from {{cookiecutter.app_name}}.tasks import enqueue

        mock_get_pool.return_value = None

        job_id = await enqueue("example_task", name="test")

        assert job_id is None

