"""
Application Factory module.

Provides the means to create a fully-configured web application instance.
"""
import asyncio
import signal

import aiohttp_cors
from aiohttp import web

from {{cookiecutter.app_name}}.core import context
from {{cookiecutter.app_name}}.core.config import get_config, get_settings, server_option
from {{cookiecutter.app_name}}.core.database import db
from {{cookiecutter.app_name}}.core.logger import get_logger
from {{cookiecutter.app_name}}.core.redis import redis_client
from {{cookiecutter.app_name}}.middleware import (
    metrics_middleware,
    rate_limit_middleware,
    request_context_middleware,
    sentry_middleware_factory,
    setup_metrics,
    setup_telemetry,
    trace_middleware,
)
from {{cookiecutter.app_name}}.core.openapi import setup_openapi_routes
from {{cookiecutter.app_name}}.routes import setup_routes

_logger = get_logger()


def get_current_request() -> str | None:
    """
    A helper function that returns the ID of the current application request from the
    context.

    :return: String or None.
    """
    request_id = context.get("X-Request-ID", None)

    if request_id:
        _logger.debug(f"Current request ID is: `{request_id}`.")
        return request_id

    _logger.warning("Request ID is missing from the context!")
    return None


async def on_app_startup(app: web.Application):
    """
    Defines the on-startup signal behavior for the application.

    :param app: The application instance the signal is being executed for.
    """
    settings = get_settings()
    host = settings.server.host
    port = settings.server.port

    # Starting up...
    app.logger.info(f"Starting up {{cookiecutter.app_name}} on address: {host}:{port}...")

    # Initialize the async database
    db.initialize()

    # Initialize Redis if enabled
    if settings.redis.enabled:
        try:
            await redis_client.initialize()
        except Exception as e:
            app.logger.warning(f"Redis initialization failed: {e}")

    # Initialize task pool for background jobs
    try:
        from {{cookiecutter.app_name}}.tasks import create_task_pool
        await create_task_pool()
    except Exception as e:
        app.logger.warning(f"Task pool initialization failed: {e}")

    # Set up telemetry
    setup_telemetry(app)

    # Set up metrics
    setup_metrics(app)

    # Started!
    app.logger.info(f"{{cookiecutter.app_name}} successfully started on {host}:{port}!")


async def on_app_cleanup(app: web.Application):
    """
    Defines the on-cleanup signal behavior for the application.

    :param app: The application instance the signal is being executed for.
    """
    # Cleaning up...
    app.logger.info("Cleaning up {{cookiecutter.app_name}}'s resources...")

    # Clean up Redis
    await redis_client.cleanup()

    # Clean up the database resources
    await db.cleanup()

    # Cleaned up!
    app.logger.info("{{cookiecutter.app_name}}'s resources were successfully cleaned up!")


async def on_app_shutdown(app: web.Application):
    """
    Defines the on-shutdown signal behavior for the application.

    :param app: The application instance the signal is being executed for.
    """
    app.logger.info("Shutting down {{cookiecutter.app_name}}...")


def setup_cors(app: web.Application) -> None:
    """
    Set up CORS for the application.
    """
    settings = get_settings()

    if not settings.cors.enabled:
        return

    # Parse allowed origins
    origins = settings.cors.origins.split(",") if settings.cors.origins != "*" else "*"

    cors = aiohttp_cors.setup(app, defaults={
        origin: aiohttp_cors.ResourceOptions(
            allow_credentials=settings.cors.allow_credentials,
            expose_headers="*",
            allow_headers="*",
            max_age=settings.cors.max_age,
        )
        for origin in (origins if isinstance(origins, list) else [origins])
    })

    # Apply CORS to all routes
    for route in list(app.router.routes()):
        try:
            cors.add(route)
        except ValueError:
            # Route already has CORS configured
            pass


def build_middlewares() -> list:
    """
    Build the list of middlewares based on configuration.
    """
    settings = get_settings()
    middlewares = []

    # Sentry error tracking (always first to catch all errors)
    middlewares.append(sentry_middleware_factory())

    # Request context (request ID, logging context)
    middlewares.append(request_context_middleware)

    # Metrics collection
    middlewares.append(metrics_middleware(
        exclude_paths=["/metrics", "/api/-/health", "/api/-/ready", "/api/-/live"]
    ))

    # OpenTelemetry tracing
    if settings.telemetry.enabled:
        middlewares.append(trace_middleware())

    # Rate limiting
    if settings.rate_limit.enabled and settings.redis.enabled:
        middlewares.append(rate_limit_middleware(
            requests=settings.rate_limit.requests,
            window=settings.rate_limit.window,
            exclude_paths=["/metrics", "/api/-/health", "/api/-/ready", "/api/-/live"],
        ))

    return middlewares


def create_app() -> web.Application:
    """
    Application factory function.

    1. Create a new application instance.
    2. Sets up routing for the application instance.
    3. Sets up CORS, metrics, and telemetry.
    4. Returns the newly created application instance.

    :return: web.Application instance
    """
    _app = web.Application(
        logger=_logger,
        middlewares=build_middlewares(),
    )
    _app['config'] = get_config()

    _app.on_startup.append(on_app_startup)
    _app.on_cleanup.append(on_app_cleanup)
    _app.on_shutdown.append(on_app_shutdown)

    # Setup views and routes
    setup_routes(_app)

    # Setup CORS
    setup_cors(_app)

    # Setup OpenAPI documentation (Swagger UI at /api/docs)
    # Routes must be registered BEFORE this call for docs to include them
    setup_openapi_routes(_app)

    return _app


def setup_graceful_shutdown(app: web.Application, runner: web.AppRunner) -> None:
    """
    Set up graceful shutdown handlers for SIGTERM and SIGINT.
    """
    shutdown_event = asyncio.Event()

    async def shutdown():
        _logger.info("Received shutdown signal, initiating graceful shutdown...")

        # Give in-flight requests time to complete
        await asyncio.sleep(5)

        # Clean up
        await runner.cleanup()
        shutdown_event.set()

    def signal_handler(sig):
        _logger.info(f"Received signal {sig.name}")
        asyncio.create_task(shutdown())

    loop = asyncio.get_event_loop()

    for sig in (signal.SIGTERM, signal.SIGINT):
        try:
            loop.add_signal_handler(sig, lambda s=sig: signal_handler(s))
        except NotImplementedError:
            # Windows doesn't support add_signal_handler
            pass


def run_app():
    """
    Application runner function.
    """
    # Install uvloop for better performance
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass

    # Create the application and read the host and port addresses
    app = create_app()
    host = server_option("host")
    port = int(server_option("port"))

    # Access Log Format
    access_log_format = '%a "%r" %s %b %Tf "%{Referrer}i" "%{User-Agent}i"'

    # Run the app using Aiohttp's web server
    web.run_app(
        app=app, host=host, port=port, access_log=_logger,
        access_log_format=access_log_format)


if __name__ == '__main__':
    run_app()
