"""
Middleware modules for Aiohttp.

Provides Sentry integration and request context management.
"""
import uuid
from collections.abc import Callable
from typing import Any

import sentry_sdk
from aiohttp import web
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from {{cookiecutter.app_name}} import APP_NAME, context
from {{cookiecutter.app_name}}.config import sentry_option
from {{cookiecutter.app_name}}.logger import bind_context, clear_context

__all__ = [
    "sentry_middleware_factory",
    "request_context_middleware",
]


def sentry_middleware_factory(sentry_kwargs: dict[str, Any] | None = None):
    """
    Aiohttp Middleware for logging error messages automatically on Sentry.
    Uses modern sentry-sdk with AioHttpIntegration.

    Args:
        sentry_kwargs: Optional configuration dictionary for Sentry SDK.
    """
    if sentry_kwargs is None:
        sentry_kwargs = {}

    dsn = sentry_option("dsn")

    # Initialize sentry-sdk with AioHttpIntegration
    sentry_sdk.init(
        dsn=dsn,
        integrations=[AioHttpIntegration()],
        traces_sample_rate=sentry_kwargs.get('traces_sample_rate', 0.0),
        **{k: v for k, v in sentry_kwargs.items() if k != 'traces_sample_rate'},
    )

    # Set the application tag for all reported events
    sentry_sdk.set_tag("app_id", APP_NAME)

    @web.middleware
    async def impl(request: web.Request, handler: Callable) -> web.Response:
        try:
            return await handler(request)
        except Exception:
            with sentry_sdk.push_scope() as scope:
                scope.set_context("request", {
                    'query_string': request.query_string,
                    'cookies': request.headers.get('Cookie', ''),
                    'headers': dict(request.headers),
                    'url': request.path,
                    'method': request.method,
                    'env': {
                        'REMOTE_ADDR': request.transport.get_extra_info('peername')[0] if request.transport else None,
                    }
                })
                sentry_sdk.capture_exception()
            raise

    return impl


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
