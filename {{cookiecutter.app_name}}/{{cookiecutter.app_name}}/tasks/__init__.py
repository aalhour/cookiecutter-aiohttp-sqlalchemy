"""
Background task processing using arq (async Redis queue).

Provides a simple interface for enqueueing and processing background jobs.
"""
from {{cookiecutter.app_name}}.tasks.worker import (
    WorkerSettings,
    create_task_pool,
    enqueue,
    get_task_pool,
)

__all__ = [
    "WorkerSettings",
    "create_task_pool",
    "get_task_pool",
    "enqueue",
]

