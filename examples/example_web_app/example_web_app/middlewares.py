"""
Sentry Middleware for Aiohttp

Source: https://github.com/underyx/aiohttp-sentry
"""

import uuid
from typing import Callable

import raven
from raven_aiohttp import AioHttpTransport
from aiohttp import web
import aiotask_context as context

from example_web_app import APP_NAME
from example_web_app.config import sentry_option


__all__ = [
    "sentry_middleware_factory",
    "request_context_middleware",
]


def sentry_middleware_factory(sentry_kwargs=None):
    """
    Aiohttp Middleware for logging error messages automatically on Sentry
    """
    if sentry_kwargs is None:
        sentry_kwargs = {}

    sentry_kwargs = {
        'dsn': sentry_option("dsn"),
        'transport': AioHttpTransport,
        'enable_breadcrumbs': False,
        **sentry_kwargs,
    }

    # Create a new raven client with the specified configuration
    _client = raven.Client(**sentry_kwargs)

    # Set the tags context with an application ID for all reported events
    _client.tags_context({"app_id": APP_NAME})

    @web.middleware
    async def impl(request: web.Request, handler: Callable) -> web.Response:
        try:
            return await handler(request)
        except:
            _client.captureException(data={
                'request': {
                    'query_string': request.query_string,
                    'cookies': request.headers.get('Cookie', ''),
                    'headers':  dict(request.headers),
                    'url': request.path,
                    'method': request.method,
                    'env': {
                        'REMOTE_ADDR': request.transport.get_extra_info('peername')[0],
                    }
                }
            })
            raise

    return impl


@web.middleware
async def request_context_middleware(request: web.Request, handler: Callable) -> web.Response:
    """
    A Middleware that sets the current request's ID in the thread-local context, this helps in getting
    the unique ID of the current request in handlers.
    """
    x_request_id_header = "X-Request-ID"
    context.set(x_request_id_header, request.headers.get(x_request_id_header, str(uuid.uuid4())))

    response = await handler(request)
    response.headers[x_request_id_header] = context.get(x_request_id_header)

    return response

