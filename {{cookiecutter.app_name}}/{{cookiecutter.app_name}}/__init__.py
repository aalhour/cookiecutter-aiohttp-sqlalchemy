"""
{{cookiecutter.project_name}}

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
APP_NAME = "{{cookiecutter.app_name}}"


# Re-export commonly used items for convenience
from {{cookiecutter.app_name}}.core import context
from {{cookiecutter.app_name}}.core.config import get_config, get_settings
from {{cookiecutter.app_name}}.core.database import db, transactional_session, Base
from {{cookiecutter.app_name}}.core.logger import get_logger
from {{cookiecutter.app_name}}.core.redis import redis_client

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
