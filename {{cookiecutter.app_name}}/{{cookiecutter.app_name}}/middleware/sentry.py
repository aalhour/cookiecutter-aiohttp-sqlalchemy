"""
Sentry error tracking middleware.

Provides automatic error reporting to Sentry.
"""
from collections.abc import Callable
from typing import Any

import sentry_sdk
from aiohttp import web
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from {{cookiecutter.app_name}} import APP_NAME
from {{cookiecutter.app_name}}.core.config import sentry_option

__all__ = [
    "sentry_middleware_factory",
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

