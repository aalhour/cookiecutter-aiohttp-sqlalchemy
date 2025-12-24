"""
Request context middleware.

Sets up request-scoped context for logging and tracking.
"""
import uuid
from collections.abc import Callable

from aiohttp import web

from {{cookiecutter.app_name}}.core import context
from {{cookiecutter.app_name}}.core.logger import bind_context, clear_context

__all__ = [
    "request_context_middleware",
]


@web.middleware
async def request_context_middleware(request: web.Request, handler: Callable) -> web.Response:
    """
    Middleware that sets up request context for logging and tracking.

    Sets the current request's ID in the context, making it available
    for structured logging and request tracking throughout the request lifecycle.
    """
    x_request_id_header = "X-Request-ID"
    request_id = request.headers.get(x_request_id_header, str(uuid.uuid4()))

    # Set in context module for backwards compatibility
    context.set(x_request_id_header, request_id)

    # Bind to structlog context for structured logging
    bind_context(
        request_id=request_id,
        method=request.method,
        path=request.path,
    )

    try:
        response = await handler(request)
        response.headers[x_request_id_header] = request_id
        return response
    finally:
        # Clear structlog context at end of request
        clear_context()

