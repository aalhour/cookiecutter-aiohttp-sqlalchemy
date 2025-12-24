"""
arq worker configuration and task pool management.
"""
import os
from typing import Any

from arq import create_pool
from arq.connections import ArqRedis, RedisSettings

from {{cookiecutter.app_name}}.core.config import get_settings
from {{cookiecutter.app_name}}.core.logger import get_logger
from {{cookiecutter.app_name}}.tasks.jobs import example_task, send_notification

__all__ = [
    "WorkerSettings",
    "create_task_pool",
    "get_task_pool",
    "enqueue",
]

_logger = get_logger()

# Global task pool
_task_pool: ArqRedis | None = None


def get_redis_settings() -> RedisSettings:
    """Get Redis settings for arq."""
    settings = get_settings()
    return RedisSettings(
        host=settings.redis.host,
        port=settings.redis.port,
        database=settings.redis.db,
        password=os.environ.get("REDIS_PASSWORD", settings.redis.password) or None,
    )


async def create_task_pool() -> ArqRedis:
    """
    Create the arq task pool for enqueueing jobs.

    Should be called during application startup.
    """
    global _task_pool
    if _task_pool is None:
        _task_pool = await create_pool(get_redis_settings())
        _logger.info("task_pool_created")
    return _task_pool


def get_task_pool() -> ArqRedis | None:
    """Get the current task pool."""
    return _task_pool


async def enqueue(
    task_name: str,
    *args: Any,
    _defer_by: int | None = None,
    _job_id: str | None = None,
    **kwargs: Any,
) -> str | None:
    """
    Enqueue a background task.

    Args:
        task_name: Name of the task function
        *args: Positional arguments for the task
        _defer_by: Seconds to delay execution
        _job_id: Optional custom job ID
        **kwargs: Keyword arguments for the task

    Returns:
        Job ID if enqueued successfully, None otherwise

    Usage:
        await enqueue("send_notification", user_id=123, message="Hello!")
        await enqueue("example_task", name="test", _defer_by=60)  # Delay 60s
    """
    pool = get_task_pool()
    if pool is None:
        _logger.warning("task_pool_not_initialized", task=task_name)
        return None

    try:
        job = await pool.enqueue_job(
            task_name,
            *args,
            _defer_by=_defer_by,
            _job_id=_job_id,
            **kwargs,
        )
        if job:
            _logger.info("task_enqueued", task=task_name, job_id=job.job_id)
            return job.job_id
        return None
    except Exception as e:
        _logger.error("task_enqueue_error", task=task_name, error=str(e))
        return None


async def startup(ctx: dict) -> None:
    """Worker startup hook."""
    _logger.info("arq_worker_starting")


async def shutdown(ctx: dict) -> None:
    """Worker shutdown hook."""
    _logger.info("arq_worker_shutdown")


class WorkerSettings:
    """
    arq worker settings.

    Run the worker with:
        arq {{cookiecutter.app_name}}.tasks.worker.WorkerSettings
    """

    redis_settings = get_redis_settings()

    # Register all task functions here
    functions = [
        example_task,
        send_notification,
    ]

    on_startup = startup
    on_shutdown = shutdown

    # Worker configuration
    max_jobs = 10
    job_timeout = 300  # 5 minutes
    keep_result = 3600  # Keep results for 1 hour
    poll_delay = 0.5  # Poll every 0.5 seconds

