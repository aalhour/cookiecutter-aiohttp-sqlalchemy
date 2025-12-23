"""
Config module using Pydantic Settings.

Provides type-safe configuration management with environment variable support.
Configuration is loaded from environment variables with optional .env file support.
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServerSettings(BaseSettings):
    """Server configuration settings."""
    model_config = SettingsConfigDict(env_prefix='SERVER_')

    host: str = "0.0.0.0"
    port: int = 9999
    scheme: str = "http"


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""
    model_config = SettingsConfigDict(env_prefix='DB_')

    host: str = "postgres"
    port: int = 5432
    user: str = "admin"
    password: str = ""
    name: str = "example_db"
    schema_: str = Field(default="public", alias="schema")
    min_connection_pool_size: int = 10
    max_connection_pool_size: int = 20
    connection_pool_recycle_time: int = 30


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    model_config = SettingsConfigDict(env_prefix='LOGGING_')

    level: str = "DEBUG"


class SentrySettings(BaseSettings):
    """Sentry configuration settings."""
    model_config = SettingsConfigDict(env_prefix='SENTRY_')

    dsn: str = ""


class Settings(BaseSettings):
    """
    Main application settings.

    All settings can be overridden via environment variables.
    Environment variables are automatically mapped using the prefixes:
    - SERVER_* for server settings
    - DB_* for database settings
    - LOGGING_* for logging settings
    - SENTRY_* for sentry settings

    Examples:
        SERVER_HOST=localhost
        SERVER_PORT=8080
        DB_HOST=postgres
        DB_PASSWORD=secret
        SENTRY_DSN=https://...
    """
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    server: ServerSettings = Field(default_factory=ServerSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    sentry: SentrySettings = Field(default_factory=SentrySettings)


@lru_cache
def get_settings() -> Settings:
    """
    Get the application settings singleton.

    Returns cached Settings instance. Uses lru_cache to ensure
    settings are only loaded once.
    """
    return Settings()


# Convenience accessors for backwards compatibility
def server_option(option: str, default: str | None = None) -> str:
    """Get a server configuration option."""
    settings = get_settings()
    return str(getattr(settings.server, option, default))


def db_option(option: str, default: str | None = None) -> str:
    """Get a database configuration option."""
    settings = get_settings()
    # Handle 'schema' -> 'schema_' field name mapping
    if option == 'schema':
        option = 'schema_'
    return str(getattr(settings.db, option, default))


def sentry_option(option: str, default: str | None = None) -> str:
    """Get a Sentry configuration option."""
    settings = get_settings()
    return str(getattr(settings.sentry, option, default))


def logging_option(option: str, default: str | None = None) -> str:
    """Get a logging configuration option."""
    settings = get_settings()
    return str(getattr(settings.logging, option, default))


# Legacy compatibility: get_config returns the Settings object
# wrapped to behave like ConfigParser for existing code
class ConfigParserAdapter:
    """Adapter to provide ConfigParser-like interface for Settings."""

    def __init__(self, settings: Settings):
        self._settings = settings

    def get(self, section: str, option: str) -> str:
        """Get a configuration value by section and option."""
        section_obj = getattr(self._settings, section.lower(), None)
        if section_obj is None:
            raise KeyError(f"Section '{section}' not found")
        # Handle 'schema' -> 'schema_' field name mapping
        if option == 'schema':
            option = 'schema_'
        value = getattr(section_obj, option, None)
        if value is None:
            raise KeyError(f"Option '{option}' not found in section '{section}'")
        return str(value)


@lru_cache
def get_config() -> ConfigParserAdapter:
    """
    Get a ConfigParser-like adapter for backwards compatibility.

    This allows existing code using config.get('section', 'option')
    to continue working without changes.
    """
    return ConfigParserAdapter(get_settings())
