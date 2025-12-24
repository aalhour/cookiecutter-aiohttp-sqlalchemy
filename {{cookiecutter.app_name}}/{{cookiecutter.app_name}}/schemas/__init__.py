"""
Pydantic schemas for request/response validation.
"""
from {{cookiecutter.app_name}}.schemas.example import (
    ExampleCreate,
    ExampleResponse,
    ExampleUpdate,
    PaginatedExamplesResponse,
)

__all__ = [
    "ExampleCreate",
    "ExampleUpdate",
    "ExampleResponse",
    "PaginatedExamplesResponse",
]

