"""
Structured logging module using structlog.

Provides structured, JSON-formatted logging with automatic context binding.
"""
import logging
import sys
from typing import Any

import structlog

from {{cookiecutter.app_name}} import APP_NAME
from {{cookiecutter.app_name}}.config import logging_option


def configure_logging() -> None:
    """
    Configure structlog with processors for structured JSON output.

    This sets up structlog to produce JSON-formatted logs with timestamps,
    log levels, and automatic exception formatting.
    """
    log_level = logging_option("level", "DEBUG")

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=getattr(logging, log_level.upper(), logging.DEBUG),
    )

    # Shared processors for both bound and stdlib loggers
    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    # Check if we're outputting to a terminal or to a file/container
    if sys.stderr.isatty():
        # Development: use colorful console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Production: use JSON output for log aggregation
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


# Configure logging on module import
configure_logging()


def get_logger(name: str = APP_NAME) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger instance.

    Returns a structlog BoundLogger that produces structured logs.
    The logger automatically includes timestamp, log level, and
    any bound context variables.

    Args:
        name: Logger name, defaults to the app name.

    Returns:
        A structlog BoundLogger instance.

    Example:
        logger = get_logger()
        logger.info("user_logged_in", user_id=123, ip_address="192.168.1.1")

        # Output (JSON in production):
        # {"timestamp": "2024-01-15T10:30:00Z", "level": "info",
        #  "event": "user_logged_in", "user_id": 123, "ip_address": "192.168.1.1"}
    """
    return structlog.get_logger(name)


def bind_context(**kwargs: Any) -> None:
    """
    Bind context variables that will be included in all subsequent log messages.

    Useful for adding request-scoped data like request_id, user_id, etc.

    Args:
        **kwargs: Key-value pairs to bind to the logging context.

    Example:
        bind_context(request_id="abc-123", user_id=456)
        logger.info("processing_request")  # Includes request_id and user_id
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """
    Clear all bound context variables.

    Should be called at the end of a request or unit of work.
    """
    structlog.contextvars.clear_contextvars()


# Legacy compatibility
def make_logger(is_development: bool = False) -> structlog.stdlib.BoundLogger:
    """
    Legacy factory function for backwards compatibility.

    Args:
        is_development: Ignored, log level is controlled by config.

    Returns:
        A structlog BoundLogger instance.
    """
    return get_logger()
