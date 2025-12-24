import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from {{cookiecutter.app_name}}.core.config import db_option

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_database_url() -> str:
    """
    Build the async database URL from the application config.
    Falls back to environment variables for Docker/CI environments.
    """
    try:
        host = db_option('host')
        port = db_option('port')
        name = db_option('name')
        user = db_option('user')
        password = os.environ.get('DB_PASSWORD', '')
    except Exception:
        # Fallback to environment variables if config is not available
        host = os.environ.get('DB_HOST', 'localhost')
        port = os.environ.get('DB_PORT', '5432')
        name = os.environ.get('DB_NAME', '{{cookiecutter.db_name}}')
        user = os.environ.get('DB_USER', '{{cookiecutter.db_user}}')
        password = os.environ.get('DB_PASSWORD', '')

    if password:
        return f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}'
    return f'postgresql+asyncpg://{user}@{host}:{port}/{name}'


def get_target_metadata():
    """
    Import and return the metadata from the application models.
    This enables autogenerate support.
    """
    try:
        from {{cookiecutter.app_name}}.core.database import Base
        return Base.metadata
    except Exception:
        return None


# Set the sqlalchemy.url in the alembic config
config.set_main_option("sqlalchemy.url", get_database_url())

target_metadata = get_target_metadata()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with a synchronous connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in async mode."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
