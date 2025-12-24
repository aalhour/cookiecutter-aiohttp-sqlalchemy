"""
SQLAlchemy model mixins for common patterns.
"""
from datetime import UTC, datetime, timedelta
from typing import Any, Self

from sqlalchemy import Boolean, DateTime, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from {{cookiecutter.app_name}}.core.logger import get_logger

__all__ = [
    "TimestampMixin",
    "SoftDeleteMixin",
]

_logger = get_logger()


class TimestampMixin:
    """
    Mixin that adds created_at and updated_at timestamps.

    Usage:
        class MyModel(Base, TimestampMixin):
            __tablename__ = "my_model"
            id: Mapped[int] = mapped_column(primary_key=True)
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(UTC),
    )


class SoftDeleteMixin:
    """
    Mixin that adds soft delete functionality.

    Instead of deleting records, marks them as deleted with a timestamp.
    Provides class methods for soft delete operations and querying.

    Usage:
        class MyModel(Base, SoftDeleteMixin):
            __tablename__ = "my_model"
            id: Mapped[int] = mapped_column(primary_key=True)

        # Soft delete a record
        await my_record.soft_delete(session)

        # Query only non-deleted records
        results = await MyModel.get_active(session)

        # Restore a soft-deleted record
        await my_record.restore(session)
    """

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
        index=True,
    )

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )

    @property
    def is_active(self) -> bool:
        """Check if record is not deleted."""
        return not self.is_deleted

    async def soft_delete(self, session: AsyncSession) -> Self:
        """
        Soft delete this record.

        Args:
            session: Database session

        Returns:
            The soft-deleted instance
        """
        self.is_deleted = True
        self.deleted_at = datetime.now(UTC)
        await session.flush()
        _logger.info(
            "record_soft_deleted",
            model=self.__class__.__name__,
            id=getattr(self, "id", None),
        )
        return self

    async def restore(self, session: AsyncSession) -> Self:
        """
        Restore a soft-deleted record.

        Args:
            session: Database session

        Returns:
            The restored instance
        """
        self.is_deleted = False
        self.deleted_at = None
        await session.flush()
        _logger.info(
            "record_restored",
            model=self.__class__.__name__,
            id=getattr(self, "id", None),
        )
        return self

    @classmethod
    async def get_active(
        cls,
        session: AsyncSession,
        **filters: Any,
    ) -> list[Self]:
        """
        Get all non-deleted records.

        Args:
            session: Database session
            **filters: Additional filter conditions

        Returns:
            List of active (non-deleted) records
        """
        query = select(cls).where(cls.is_deleted == False)  # noqa: E712
        for key, value in filters.items():
            if hasattr(cls, key):
                query = query.where(getattr(cls, key) == value)
        result = await session.execute(query)
        return list(result.scalars().all())

    @classmethod
    async def get_deleted(
        cls,
        session: AsyncSession,
    ) -> list[Self]:
        """
        Get all soft-deleted records.

        Args:
            session: Database session

        Returns:
            List of deleted records
        """
        result = await session.execute(
            select(cls).where(cls.is_deleted == True)  # noqa: E712
        )
        return list(result.scalars().all())

    @classmethod
    async def hard_delete(
        cls,
        session: AsyncSession,
        id_: int,
    ) -> bool:
        """
        Permanently delete a record (use with caution).

        Args:
            session: Database session
            id_: Record ID to delete

        Returns:
            True if deleted, False if not found
        """
        result = await session.execute(
            delete(cls).where(cls.id == id_)  # type: ignore
        )
        deleted = result.rowcount > 0
        if deleted:
            _logger.info(
                "record_hard_deleted",
                model=cls.__name__,
                id=id_,
            )
        return deleted

    @classmethod
    async def purge_deleted(
        cls,
        session: AsyncSession,
        older_than_days: int = 30,
    ) -> int:
        """
        Permanently delete all soft-deleted records older than specified days.

        Args:
            session: Database session
            older_than_days: Delete records soft-deleted more than this many days ago

        Returns:
            Number of records deleted
        """
        cutoff = datetime.now(UTC) - timedelta(days=older_than_days)
        result = await session.execute(
            delete(cls).where(
                cls.is_deleted == True,  # noqa: E712
                cls.deleted_at < cutoff,
            )
        )
        count = result.rowcount
        if count > 0:
            _logger.info(
                "records_purged",
                model=cls.__name__,
                count=count,
                older_than_days=older_than_days,
            )
        return count

