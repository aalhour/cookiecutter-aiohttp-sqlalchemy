"""
Context management module using Python's native contextvars.

Provides request-scoped context variables for async handlers.
"""

import contextvars
from typing import Optional, Any


# Context variable for the current request ID
_request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar('request_id', default=None)


def get(key: str, default: Any = None) -> Any:
    """
    Get a context variable value.
    Currently only supports 'X-Request-ID'.
    """
    if key == "X-Request-ID":
        return _request_id_var.get() or default
    return default


def set(key: str, value: Any) -> None:
    """
    Set a context variable value.
    Currently only supports 'X-Request-ID'.
    """
    if key == "X-Request-ID":
        _request_id_var.set(value)


def get_request_id() -> Optional[str]:
    """Get the current request ID."""
    return _request_id_var.get()


def set_request_id(request_id: str) -> contextvars.Token:
    """Set the current request ID and return a token for resetting."""
    return _request_id_var.set(request_id)

