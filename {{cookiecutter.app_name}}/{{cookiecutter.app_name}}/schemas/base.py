"""
Base schemas and utilities for Pydantic models.
"""
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
        ser_json_timedelta="iso8601",
    )

    def to_json_dict(self) -> dict[str, Any]:
        """Serialize to JSON-compatible dict (datetimes as ISO strings)."""
        return self.model_dump(mode="json")


class ErrorResponse(BaseSchema):
    """Standard error response schema."""

    error: str
    message: str
    details: dict[str, Any] | None = None


class MessageResponse(BaseSchema):
    """Simple message response schema."""

    message: str


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response wrapper."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class HealthResponse(BaseSchema):
    """Health check response schema."""

    status: str
    timestamp: datetime
    version: str
    checks: dict[str, dict[str, Any]] | None = None


class ReadinessResponse(BaseSchema):
    """Readiness check response schema."""

    ready: bool
    checks: dict[str, bool]

