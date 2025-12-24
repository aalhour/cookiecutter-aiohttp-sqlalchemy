"""
Pydantic schemas for Example API request/response validation.
"""
from datetime import datetime
from decimal import Decimal

from pydantic import Field, field_validator

from {{cookiecutter.app_name}}.schemas.base import BaseSchema, PaginatedResponse


class ExampleCreate(BaseSchema):
    """Schema for creating a new Example."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Name of the example (required)",
        examples=["My Example Item"],
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
        description="Optional description text",
        examples=["A detailed description of the item"],
    )
    price: Decimal | None = Field(
        default=None,
        ge=0,
        le=999999.99,
        description="Price (must be non-negative)",
        examples=[19.99],
    )
    is_active: bool = Field(
        default=True,
        description="Whether the item is active",
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """Ensure name is not just whitespace."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip()


class ExampleUpdate(BaseSchema):
    """Schema for updating an existing Example."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated name",
    )
    description: str | None = Field(
        default=None,
        max_length=5000,
        description="Updated description",
    )
    price: Decimal | None = Field(
        default=None,
        ge=0,
        le=999999.99,
        description="Updated price",
    )
    is_active: bool | None = Field(
        default=None,
        description="Updated active status",
    )

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        """Ensure name is not just whitespace if provided."""
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty or whitespace")
        return v.strip() if v else v


class ExampleResponse(BaseSchema):
    """Schema for Example response data."""

    id: str = Field(description="Unique identifier")
    name: str = Field(description="Name of the example")
    description: str | None = Field(description="Description text")
    price: float | None = Field(description="Price value")
    is_active: bool = Field(description="Active status")
    created_at: datetime | None = Field(description="Creation timestamp")
    updated_at: datetime | None = Field(description="Last update timestamp")

    @classmethod
    def from_orm_dict(cls, data: dict) -> "ExampleResponse":
        """Create response from ORM serialized dict."""
        return cls(**data)


class PaginatedExamplesResponse(PaginatedResponse[ExampleResponse]):
    """Paginated response for Example list."""

    pass

