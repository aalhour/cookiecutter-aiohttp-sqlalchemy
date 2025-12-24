"""
Example Web App

A modern async web API built with aiohttp and SQLAlchemy 2.0.
"""
###
# Application Version
#
__version__ = "1.0"


###
# Application Name
# This constant is also used by Sentry for tagging all errors reported by this component
#
APP_NAME = "example_web_app"


# Re-export commonly used items for convenience
from example_web_app.core import context
from example_web_app.core.config import get_config, get_settings
from example_web_app.core.database import db, transactional_session, Base
from example_web_app.core.logger import get_logger
from example_web_app.core.redis import redis_client

__all__ = [
    "__version__",
    "APP_NAME",
    "context",
    "get_config",
    "get_settings",
    "db",
    "transactional_session",
    "Base",
    "get_logger",
    "redis_client",
]
