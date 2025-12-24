"""
Core infrastructure and configuration.

This package contains the foundational components:
- config: Application settings (Pydantic Settings)
- context: Request-scoped context variables
- database: SQLAlchemy async engine and session management
- logger: Structured logging with structlog
- redis: Redis client for caching and rate limiting
- cache: Caching decorator and utilities
- websocket: WebSocket connection management
"""
from example_web_app.core.config import (
    get_config,
    get_settings,
    db_option,
    logging_option,
    sentry_option,
    server_option,
)
from example_web_app.core.context import (
    get_request_id,
    set_request_id,
)
from example_web_app.core.database import db, transactional_session, Base
from example_web_app.core.logger import get_logger, bind_context, clear_context
from example_web_app.core.redis import redis_client, get_redis
from example_web_app.core.cache import cache, invalidate_cache
from example_web_app.core.websocket import (
    WebSocketManager,
    ws_manager,
    websocket_handler,
    send_notification,
)

__all__ = [
    # Config
    "get_config",
    "get_settings",
    "db_option",
    "logging_option",
    "sentry_option",
    "server_option",
    # Context
    "get_request_id",
    "set_request_id",
    # Database
    "db",
    "transactional_session",
    "Base",
    # Logger
    "get_logger",
    "bind_context",
    "clear_context",
    # Redis
    "redis_client",
    "get_redis",
    # Cache
    "cache",
    "invalidate_cache",
    # WebSocket
    "WebSocketManager",
    "ws_manager",
    "websocket_handler",
    "send_notification",
]
