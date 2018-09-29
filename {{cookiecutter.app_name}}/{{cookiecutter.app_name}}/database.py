"""
Database module.

Defines types, functions and primitives for the initialization, disposition and management of
  database connections and their sessions.
"""
import os
import importlib.util
from pathlib import Path
from typing import Callable

from sqlalchemy import create_engine as _sa_create_engine
from sqlalchemy.schema import MetaData
from sqlalchemy.engine.base import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session as SQLAlchemySession

from {{cookiecutter.app_name}}.config import db_option
from {{cookiecutter.app_name}}.background import run_async
from {{cookiecutter.app_name}}.logger import get_logger
from {{cookiecutter.app_name}}.models.base import BaseModelMixin


__all__ = [
    "transactional_session",
    "DatabaseManager",
    "db",
]


_logger = get_logger()


###
# Common Errors
#
class DatabaseNotInitialized(Exception):
    def __init__(self, *args, **kwargs):
        super(DatabaseNotInitialized, self).__init__(args, kwargs)


###
# Context Manager for Transactional Session Management
#
class transactional_session:
    """
    Context manager which provides transactional session management.
    Supports the sync/async context manager protocols.
    """
    def __init__(self, expire_on_commit: bool = True):
        """
        Initializer.
        :param bool expire_on_commit: If True, will make a session the expires all objects in memory after commit;
            otherwise, will make objects in memory accessible even after session.commit() is called.
        """
        if db.Session is None or db.OnCommitExpiringSession is None:
            raise DatabaseNotInitialized("The global database.db singleton is not initialized!")

        self._session = None
        self._expire_on_commit = expire_on_commit

    ###
    # Synchronous context manager protocol
    #
    def __enter__(self) -> SQLAlchemySession:
        if self._expire_on_commit is True:
            self._session = db.OnCommitExpiringSession()
        else:
            self._session = db.Session()

        return self._session

    def __exit__(self, exc_type, exc, tb):
        try:
            self._session.commit()
        except Exception as e:
            self._session.rollback()
            _logger.error(e)
            raise e
        finally:
            self._session.close()

    ###
    # Asynchronous context manager protocol
    #
    async def __aenter__(self) -> SQLAlchemySession:
        if self._expire_on_commit is True:
            self._session = db.OnCommitExpiringSession()
        else:
            self._session = db.Session()

        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        try:
            await run_async(self._session.commit)
        except Exception as e:
            await run_async(self._session.rollback)
            _logger.error(e)
            raise e
        finally:
            self._session.close()


###
# Database Manager
#
class DatabaseManager:
    """
    Configuration class for DB that encapsulates engine and configured class for creating scoped session instances.
    """
    def __init__(self):
        ###
        # Private database engine and metadata attributes.
        #
        self._engine = None
        self._metadata = MetaData(schema=db_option('schema'))

        ###
        # Session Factory classes, later initialized in self.initialize() method.
        #
        # The self.Session corresponds to a session factory that doesn't expire ORM instances from memory
        #   after getting committed.
        #
        # The self.OnCommitExpiringSession corresponds to a session factory that expires ORM instances from
        #   memory after getting committed.
        #
        self.Session = None
        self.OnCommitExpiringSession = None

        ###
        # Declarative Base Model class.
        #
        self.BaseModel = declarative_base(
            cls=BaseModelMixin,
            metadata=MetaData(schema=db_option('schema')))

    @property
    def engine(self) -> Engine:
        return self._engine

    @classmethod
    def create_database_engine(cls) -> Engine:
        """
        Creates a new SQLAlchemy database engine (sqlalchemy.engine.base.Engine) and returns it.

        :return: a working SQLAlchemy database engine
        """
        ###
        # Database configuration options
        #
        # Database connection settings
        cfg_host = db_option('host')
        cfg_port = db_option('port')
        cfg_dbname = db_option('name')
        cfg_user = db_option('user')

        # Database connection pool settings
        min_pool_size = int(db_option('min_connection_pool_size'))
        max_pool_size = int(db_option('max_connection_pool_size'))

        if max_pool_size < min_pool_size:
            raise ValueError("Max Pool Size cannot be lower than Min Pool Size!")

        max_pool_overflow = max_pool_size - min_pool_size
        pool_recycle_time = int(db_option('connection_pool_recycle_time'))

        # Database connection string
        db_uri = f'postgresql://{cfg_user}@{cfg_host}:{cfg_port}/{cfg_dbname}'

        return _sa_create_engine(
            db_uri, encoding='utf-8', pool_size=min_pool_size, max_overflow=max_pool_overflow,
            pool_recycle=pool_recycle_time)

    def initialize(self, db_engine: Engine=None, scope_function: Callable = None):
        """
        Configure class for creating scoped sessions.

        :param db_engine: DB connection engine.
        :param scope_function: a function for scoping database connections.
        """
        # Set or initialize the database engine
        if db_engine is None:
            self._engine = self.create_database_engine()
        else:
            self._engine = db_engine

        # Create the session factory classes
        self.Session = scoped_session(
            sessionmaker(bind=self._engine, expire_on_commit=False),
            scopefunc=scope_function)

        self.OnCommitExpiringSession = scoped_session(
            sessionmaker(bind=self._engine, expire_on_commit=True),
            scopefunc=scope_function)

        # Import all model modules. SQLAlchemy doesn't do auto-discovery, so relationships don't
        # work if we don't import them all before usage.
        # Also I can't just do `from {{cookiecutter.app_name}}.models import *` here, because in py3, the * is only
        # allowed at the module level
        import_all_models()

    def cleanup(self):
        """
        Cleans up the database connection pool.
        """
        if self._engine is not None:
            self._engine.dispose()


def _package_contents(package_name):
    """
    Given a package name ('{{cookiecutter.app_name}}.models') will return all the modules in that package
    Source: https://stackoverflow.com/questions/487971/is-there-a-standard-way-to-list-names-of-python-modules-in-a-package
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
    SQLAlchemy doesn't auto-discover models.
    Models with relationships don't work if we don't load all the modules involved in the relationship
    Basically all our models are related via relationships
    We therefore besicaly need to import all model modules manually before using any of them
    """
    for full_module_name in _package_contents('{{cookiecutter.app_name}}.models'):
        importlib.import_module(full_module_name)


###
# Database Extension
#
db = DatabaseManager()

