"""
Background job definitions.

Define your async background tasks here.
"""
import asyncio
from typing import Any

from example_web_app.core.logger import get_logger

__all__ = [
    "example_task",
    "send_notification",
]

_logger = get_logger()


async def example_task(ctx: dict, name: str, data: dict | None = None) -> dict[str, Any]:
    """
    Example background task.

    Args:
        ctx: arq context (contains redis connection)
        name: Task name for logging
        data: Optional data to process

    Returns:
        Result dictionary
    """
    _logger.info("example_task_started", name=name, data=data)

    # Simulate some work
    await asyncio.sleep(1)

    result = {
        "name": name,
        "processed": True,
        "data": data,
    }

    _logger.info("example_task_completed", name=name)
    return result


async def send_notification(
    ctx: dict,
    user_id: int,
    message: str,
    channel: str = "email",
) -> dict[str, Any]:
    """
    Send a notification to a user.

    Args:
        ctx: arq context
        user_id: The user to notify
        message: Notification message
        channel: Notification channel (email, sms, push)

    Returns:
        Result with notification status
    """
    _logger.info(
        "notification_sending",
        user_id=user_id,
        channel=channel,
    )

    # Simulate sending notification
    await asyncio.sleep(0.5)

    # In a real app, this would:
    # - Look up user's contact info
    # - Send via appropriate channel (email, SMS, push, etc.)
    # - Handle retries and failures

    _logger.info(
        "notification_sent",
        user_id=user_id,
        channel=channel,
    )

    return {
        "user_id": user_id,
        "channel": channel,
        "status": "sent",
    }

