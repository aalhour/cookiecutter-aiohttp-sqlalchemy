"""
Sentry Middleware for Aiohttp

Source: https://docs.sentry.io/platforms/python/integrations/aiohttp/
"""

import uuid
from typing import Callable

import sentry_sdk
from sentry_sdk.integrations.aiohttp import AioHttpIntegration
from aiohttp import web

from example_web_app import APP_NAME
from example_web_app.config import sentry_option
from example_web_app import context


__all__ = [
    "sentry_middleware_factory",
    "request_context_middleware",
]


def sentry_middleware_factory(sentry_kwargs=None):
    """
    Aiohttp Middleware for logging error messages automatically on Sentry.
    Uses modern sentry-sdk with AioHttpIntegration.
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
    A Middleware that sets the current request's ID in the context, this helps in getting
    the unique ID of the current request in handlers.
    """
    x_request_id_header = "X-Request-ID"
    request_id = request.headers.get(x_request_id_header, str(uuid.uuid4()))
    context.set(x_request_id_header, request_id)

    response = await handler(request)
    response.headers[x_request_id_header] = context.get(x_request_id_header)

    return response
