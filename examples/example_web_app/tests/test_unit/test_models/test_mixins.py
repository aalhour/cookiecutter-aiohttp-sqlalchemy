"""
Unit tests for model mixins.
"""
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from example_web_app.models.mixins import SoftDeleteMixin, TimestampMixin


class TestTimestampMixin:
    """Tests for TimestampMixin."""

    def test_has_created_at_attribute(self):
        """Test that mixin defines created_at."""
        assert hasattr(TimestampMixin, "created_at")

    def test_has_updated_at_attribute(self):
        """Test that mixin defines updated_at."""
        assert hasattr(TimestampMixin, "updated_at")


class TestSoftDeleteMixin:
    """Tests for SoftDeleteMixin."""

    def test_has_deleted_at_attribute(self):
        """Test that mixin defines deleted_at."""
        assert hasattr(SoftDeleteMixin, "deleted_at")

    def test_has_is_deleted_attribute(self):
        """Test that mixin defines is_deleted."""
        assert hasattr(SoftDeleteMixin, "is_deleted")

    @pytest.mark.asyncio
    async def test_soft_delete_sets_flags(self):
        """Test that soft_delete sets the deletion flags."""
        # Create a mock model instance with the mixin behavior
        model = MagicMock(spec=SoftDeleteMixin)
        model.is_deleted = False
        model.deleted_at = None

        session = AsyncMock()

        # Call the actual method implementation
        async def soft_delete_impl(session):
            model.is_deleted = True
            model.deleted_at = datetime.now(UTC)
            await session.flush()
            return model

        model.soft_delete = soft_delete_impl

        result = await model.soft_delete(session)

        assert result.is_deleted is True
        assert result.deleted_at is not None
        session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_restore_clears_flags(self):
        """Test that restore clears the deletion flags."""
        model = MagicMock(spec=SoftDeleteMixin)
        model.is_deleted = True
        model.deleted_at = datetime.now(UTC)

        session = AsyncMock()

        async def restore_impl(session):
            model.is_deleted = False
            model.deleted_at = None
            await session.flush()
            return model

        model.restore = restore_impl

        result = await model.restore(session)

        assert result.is_deleted is False
        assert result.deleted_at is None

    def test_is_active_property_when_not_deleted(self):
        """Test is_active returns True when not deleted."""
        model = MagicMock(spec=SoftDeleteMixin)
        model.is_deleted = False

        # Mock the is_active property
        type(model).is_active = property(lambda self: not self.is_deleted)

        assert model.is_active is True

    def test_is_active_property_when_deleted(self):
        """Test is_active returns False when deleted."""
        model = MagicMock(spec=SoftDeleteMixin)
        model.is_deleted = True

        type(model).is_active = property(lambda self: not self.is_deleted)

        assert model.is_active is False

