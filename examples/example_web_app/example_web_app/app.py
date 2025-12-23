"""
Application Factory module.

Provides the means to create a fully-configured web application instance.
"""

from pathlib import Path, PurePath
from typing import Optional

from aiohttp import web
from aiohttp_swagger import setup_swagger

from example_web_app.config import get_config, server_option
from example_web_app.database import db
from example_web_app.middlewares import sentry_middleware_factory, request_context_middleware
from example_web_app.routes import setup_routes
from example_web_app.logger import get_logger
from example_web_app import context


_logger = get_logger()


def get_current_request() -> Optional[str]:
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
    Defines the on-startup signal behavior for the application. The app parameter is
      important for aiohttp's Signal interface.

    :param app: The application instance the signal is being executed for.
    """
    host = app["config"].get("server", "host")
    port = app["config"].get("server", "port")

    # Starting up...
    app.logger.info("Starting up example_web_app on address: {host}:{port}...".format(host=host, port=port))

    # Initialize the database with the `get_current_request` function as the scoping function
    # so that all SQLAlchemy DB sessions are created within the handler's current request context.
    db.initialize(scope_function=get_current_request)

    # Started!
    app.logger.info("example_web_app successfully started on {host}:{port}!".format(host=host, port=port))


async def on_app_cleanup(app: web.Application):
    """
    Defines the on-cleanup signal behavior for the application. The app parameter is
      important for aiohttp's Signal interface.

    :param app: The application instance the signal is being executed for.
    """
    # Cleaning up...
    app.logger.info("Cleaning up example_web_app's resources...")

    # Clean up the database resources
    db.cleanup()

    # Cleaned up!
    app.logger.info("example_web_app's resources were successfully cleaned up!")


async def on_app_shutdown(app: web.Application):
    """
    Defines the on-shutdown signal behavior for the application. The app parameter is
      important for aiohttp's Signal interface.

    :param app: The application instance the signal is being executed for.
    """
    app.logger.info("Shutting down example_web_app...")


def create_app() -> web.Application:
    """
    Application factory function. It does the following:
        1. Create a new application instance.
        2. Initializes the global DB_ENGINE constant variable.
        3. Sets up routing for the application instance.
        4. Sets up the Swagger plugin.
        5. Returns the newly created application instance.

    :return: web.Application instance
    """
    ###
    # Create an app instance and do the following:
    #   1. Initialize its config.
    #   2. Prepare its on-startup, on-cleanup and on-shutdown signals.
    #
    _app = web.Application(
        logger=_logger,
        middlewares=[
            sentry_middleware_factory(),
            request_context_middleware,
        ],
    )
    _app['config'] = get_config()

    _app.on_startup.append(on_app_startup)
    _app.on_cleanup.append(on_app_cleanup)
    _app.on_shutdown.append(on_app_shutdown)

    ###
    # Setup views and routes
    #
    setup_routes(_app)

    ###
    # Setup the swagger /docs endpoint.
    #
    this_modules_path = Path(__file__).parent.absolute()
    api_v1_0_swagger_doc_path = str(PurePath(this_modules_path, "docs/swagger-v1.0.yaml"))
    setup_swagger(_app, swagger_url="/api/v1.0/docs", swagger_from_file=api_v1_0_swagger_doc_path)

    return _app


def run_app():
    """
    Application runner function.
    """
    # Install uvloop for better performance (only when running the app directly)
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass

    ###
    # Create the application and read the host and port addresses
    #
    app = create_app()
    host = server_option("host")
    port = int(server_option("port"))

    ###
    # Access Log Format (Will not work with the dev server(for now))
    #
    # %a: Remote IP-address
    # %r: First line of request
    # %s: Response status code
    # %b: Size of response in bytes, excluding HTTP headers
    # %Tf: The time taken to serve the request, in seconds with fraction in %.06f format
    #
    access_log_format = '%a "%r" %s %b %Tf "%{Referrer}i" "%{User-Agent}i"'

    ###
    # Run the app using Aiohttp's web server
    #
    web.run_app(
        app=app, host=host, port=port, access_log=_logger,
        access_log_format=access_log_format)


if __name__ == '__main__':
    run_app()
