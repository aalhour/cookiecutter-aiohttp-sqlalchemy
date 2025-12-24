"""
Unit tests for Example Pydantic schemas.

Tests validation rules for request/response schemas.
"""
from datetime import datetime
from decimal import Decimal

import pytest
from pydantic import ValidationError

from example_web_app.schemas.example import (
    ExampleCreate,
    ExampleResponse,
    ExampleUpdate,
)


class TestExampleCreateSchema:
    """Tests for ExampleCreate schema validation."""

    def test_valid_create_with_all_fields(self):
        """Test creating with all valid fields."""
        data = ExampleCreate(
            name="Test Example",
            description="A test description",
            price=Decimal("19.99"),
            is_active=True,
        )
        assert data.name == "Test Example"
        assert data.description == "A test description"
        assert data.price == Decimal("19.99")
        assert data.is_active is True

    def test_valid_create_with_required_only(self):
        """Test creating with only required fields."""
        data = ExampleCreate(name="Test Example")
        assert data.name == "Test Example"
        assert data.description is None
        assert data.price is None
        assert data.is_active is True  # default

    def test_name_is_required(self):
        """Test that name is required."""
        with pytest.raises(ValidationError) as exc_info:
            ExampleCreate()
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("name",) for e in errors)

    def test_name_cannot_be_empty(self):
        """Test that name cannot be empty string."""
        with pytest.raises(ValidationError) as exc_info:
            ExampleCreate(name="")
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_name_cannot_be_whitespace_only(self):
        """Test that name cannot be just whitespace."""
        with pytest.raises(ValidationError) as exc_info:
            ExampleCreate(name="   ")
        errors = exc_info.value.errors()
        assert len(errors) > 0

    def test_name_is_stripped(self):
        """Test that name is stripped of whitespace."""
        data = ExampleCreate(name="  Test Example  ")
        assert data.name == "Test Example"

    def test_name_max_length(self):
        """Test name max length validation."""
        with pytest.raises(ValidationError):
            ExampleCreate(name="x" * 256)  # Max is 255

    def test_price_must_be_non_negative(self):
        """Test that price must be >= 0."""
        with pytest.raises(ValidationError):
            ExampleCreate(name="Test", price=Decimal("-1.00"))

    def test_price_zero_is_valid(self):
        """Test that price can be zero."""
        data = ExampleCreate(name="Test", price=Decimal("0"))
        assert data.price == Decimal("0")

    def test_price_max_value(self):
        """Test price max value validation."""
        with pytest.raises(ValidationError):
            ExampleCreate(name="Test", price=Decimal("1000000.00"))


class TestExampleUpdateSchema:
    """Tests for ExampleUpdate schema validation."""

    def test_all_fields_optional(self):
        """Test that all fields are optional for updates."""
        data = ExampleUpdate()
        assert data.name is None
        assert data.description is None
        assert data.price is None
        assert data.is_active is None

    def test_partial_update(self):
        """Test updating with only some fields."""
        data = ExampleUpdate(name="Updated Name")
        assert data.name == "Updated Name"
        assert data.description is None

    def test_name_validation_still_applies(self):
        """Test that name validation still applies if provided."""
        with pytest.raises(ValidationError):
            ExampleUpdate(name="")

    def test_price_validation_still_applies(self):
        """Test that price validation still applies if provided."""
        with pytest.raises(ValidationError):
            ExampleUpdate(price=Decimal("-1.00"))


class TestExampleResponseSchema:
    """Tests for ExampleResponse schema."""

    def test_from_orm_dict(self):
        """Test creating response from ORM dict."""
        orm_data = {
            "id": "1",
            "name": "Test Example",
            "description": "A description",
            "price": 19.99,
            "is_active": True,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": None,
        }
        response = ExampleResponse.from_orm_dict(orm_data)
        assert response.id == "1"
        assert response.name == "Test Example"
        assert response.price == 19.99
        assert response.is_active is True

    def test_model_dump(self):
        """Test serialization to dict."""
        orm_data = {
            "id": "1",
            "name": "Test Example",
            "description": None,
            "price": None,
            "is_active": True,
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": None,
        }
        response = ExampleResponse.from_orm_dict(orm_data)
        data = response.model_dump()

        assert data["id"] == "1"
        assert data["name"] == "Test Example"
        assert data["description"] is None

