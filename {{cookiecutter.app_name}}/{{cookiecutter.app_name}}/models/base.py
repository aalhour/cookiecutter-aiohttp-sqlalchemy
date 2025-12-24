"""
Base Models module

This module re-exports the Base class from the database module for convenience.
"""

from {{cookiecutter.app_name}}.core.database import Base

__all__ = [
    "Base",
]
