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


class RedisSettings(BaseSettings):
    """Redis configuration settings."""
    model_config = SettingsConfigDict(env_prefix='REDIS_')

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: str = ""
    max_connections: int = 10
    enabled: bool = True


class LoggingSettings(BaseSettings):
    """Logging configuration settings."""
    model_config = SettingsConfigDict(env_prefix='LOGGING_')

    level: str = "DEBUG"


class SentrySettings(BaseSettings):
    """Sentry configuration settings."""
    model_config = SettingsConfigDict(env_prefix='SENTRY_')

    dsn: str = ""


class TelemetrySettings(BaseSettings):
    """OpenTelemetry configuration settings."""
    model_config = SettingsConfigDict(env_prefix='OTEL_')

    enabled: bool = False
    service_name: str = "example_web_app"
    otlp_endpoint: str = ""
    otlp_insecure: bool = True


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration settings."""
    model_config = SettingsConfigDict(env_prefix='RATELIMIT_')

    enabled: bool = True
    requests: int = 100
    window: int = 60  # seconds


class CorsSettings(BaseSettings):
    """CORS configuration settings."""
    model_config = SettingsConfigDict(env_prefix='CORS_')

    enabled: bool = True
    origins: str = "*"  # Comma-separated list of allowed origins
    allow_credentials: bool = True
    max_age: int = 3600


class Settings(BaseSettings):
    """
    Main application settings.

    All settings can be overridden via environment variables.
    Environment variables are automatically mapped using the prefixes:
    - SERVER_* for server settings
    - DB_* for database settings
    - REDIS_* for redis settings
    - LOGGING_* for logging settings
    - SENTRY_* for sentry settings
    - OTEL_* for OpenTelemetry settings
    - RATELIMIT_* for rate limiting settings
    - CORS_* for CORS settings

    Examples:
        SERVER_HOST=localhost
        SERVER_PORT=8080
        DB_HOST=postgres
        DB_PASSWORD=secret
        REDIS_HOST=redis
        REDIS_PASSWORD=redispass
        SENTRY_DSN=https://...
        OTEL_ENABLED=true
        OTEL_OTLP_ENDPOINT=http://otel-collector:4317
    """
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    server: ServerSettings = Field(default_factory=ServerSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    sentry: SentrySettings = Field(default_factory=SentrySettings)
    telemetry: TelemetrySettings = Field(default_factory=TelemetrySettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)


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

