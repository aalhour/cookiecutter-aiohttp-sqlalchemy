"""
Database module.

Defines types, functions and primitives for the initialization, disposition and management of
async database connections and sessions using SQLAlchemy 2.0.
"""
import importlib.util
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from {{cookiecutter.app_name}}.core.config import db_option
from {{cookiecutter.app_name}}.core.logger import get_logger

__all__ = [
    "Base",
    "get_session",
    "transactional_session",
    "DatabaseManager",
    "db",
]


_logger = get_logger()


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 declarative base class."""
    metadata = MetaData(schema=db_option('schema'))


class DatabaseNotInitialized(Exception):
    """Raised when database operations are attempted before initialization."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DatabaseManager:
    """
    Configuration class for DB that encapsulates async engine and session maker.
    """
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._session_maker: async_sessionmaker[AsyncSession] | None = None

    @property
    def engine(self) -> AsyncEngine | None:
        return self._engine

    @property
    def session_maker(self) -> async_sessionmaker[AsyncSession] | None:
        return self._session_maker

    def get_database_url(self) -> str:
        """
        Build the async database URL from configuration.
        """
        host = db_option('host')
        port = db_option('port')
        name = db_option('name')
        user = db_option('user')
        password = os.environ.get('DB_PASSWORD', '')

        if password:
            return f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}'
        return f'postgresql+asyncpg://{user}@{host}:{port}/{name}'

    def initialize(self, db_url: str | None = None):
        """
        Initialize the async database engine and session maker.

        :param db_url: Optional database URL. If not provided, builds from config.
        """
        if db_url is None:
            db_url = self.get_database_url()

        # Connection pool settings
        min_pool_size = int(db_option('min_connection_pool_size'))
        max_pool_size = int(db_option('max_connection_pool_size'))

        if max_pool_size < min_pool_size:
            raise ValueError("Max Pool Size cannot be lower than Min Pool Size!")

        pool_recycle_time = int(db_option('connection_pool_recycle_time'))

        self._engine = create_async_engine(
            db_url,
            pool_size=min_pool_size,
            max_overflow=max_pool_size - min_pool_size,
            pool_recycle=pool_recycle_time,
            echo=False,
        )

        self._session_maker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Import all model modules for relationship discovery
        import_all_models()

        _logger.info(f"Database initialized with engine: {db_url.split('@')[-1]}")

    async def cleanup(self):
        """
        Clean up database connections.
        """
        if self._engine is not None:
            await self._engine.dispose()
            _logger.info("Database engine disposed")


# Global database manager instance
db = DatabaseManager()


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager that yields a database session.

    Usage:
        async with get_session() as session:
            result = await session.execute(select(Model))
    """
    if db.session_maker is None:
        raise DatabaseNotInitialized("Database not initialized. Call db.initialize() first.")

    async with db.session_maker() as session:
        yield session


@asynccontextmanager
async def transactional_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager that provides transactional session management.
    Automatically commits on success, rolls back on exception.

    Usage:
        async with transactional_session() as session:
            session.add(new_record)
            # Auto-commits on exit, auto-rollbacks on exception
    """
    if db.session_maker is None:
        raise DatabaseNotInitialized("Database not initialized. Call db.initialize() first.")

    async with db.session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            _logger.error(f"Transaction rolled back: {e}")
            raise


def _package_contents(package_name: str) -> set[str]:
    """
    Given a package name ('{{cookiecutter.app_name}}.models') will return all the modules in that package.
    """
    spec = importlib.util.find_spec(package_name)
    if spec is None:
        return set()

    pathname = Path(spec.origin).parent
    ret = set()
    with os.scandir(pathname) as entries:
        for entry in entries:
            if entry.name.startswith('__'):
                continue
            current = '.'.join((package_name, entry.name.partition('.')[0]))
            if entry.is_file():
                if entry.name.endswith('.py'):
                    ret.add(current)
            elif entry.is_dir():
                ret.add(current)
                ret |= _package_contents(current)

    return ret


def import_all_models():
    """
    Import all model modules for SQLAlchemy relationship discovery.
    """
    for full_module_name in _package_contents('{{cookiecutter.app_name}}.models'):
        importlib.import_module(full_module_name)

