"""
Example model demonstrating SQLAlchemy 2.0 async patterns with full CRUD operations.
"""
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from example_web_app.core.database import Base
from example_web_app.core.logger import get_logger

__all__ = [
    "Example",
]


_logger = get_logger()


class Example(Base):
    """
    Data model for Example DB table using SQLAlchemy 2.0 mapped columns.

    Demonstrates a complete model with:
    - Multiple field types (string, text, numeric, boolean)
    - Automatic timestamps (created_at, updated_at)
    - Full CRUD operations (Create, Read, Update, Delete)
    """
    __tablename__ = 'example'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=lambda: datetime.now(UTC)
    )

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        price: float | None = None,
        is_active: bool = True,
        id_: int | None = None,
    ):
        """
        New model instance initializer.

        Args:
            name: The name of the example (required)
            description: Optional description text
            price: Optional price as decimal
            is_active: Whether the item is active (defaults to True)
            id_: Optional ID (usually auto-generated)
        """
        if id_ is not None:
            self.id = id_
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if price is not None:
            self.price = price
        self.is_active = is_active

    # ==================== READ OPERATIONS ====================

    @classmethod
    async def get_by_id(cls, id_: int | str, session: AsyncSession) -> "Example | None":
        """
        Returns a record by ID using SQLAlchemy 2.0 async query.

        Args:
            id_: The ID of the record
            session: AsyncSession instance

        Returns:
            The specified Example by id or None
        """
        result = await session.execute(
            select(cls).where(cls.id == int(id_))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession, active_only: bool = False) -> list["Example"]:
        """
        Returns all records in the table.

        Args:
            session: AsyncSession instance
            active_only: If True, only return active items

        Returns:
            List of all examples in the database
        """
        query = select(cls)
        if active_only:
            query = query.where(cls.is_active == True)  # noqa: E712
        result = await session.execute(query)
        return list(result.scalars().all())

    # ==================== CREATE OPERATIONS ====================

    @classmethod
    async def create(
        cls,
        session: AsyncSession,
        name: str,
        description: str | None = None,
        price: float | None = None,
        is_active: bool = True,
    ) -> "Example":
        """
        Create a new Example record.

        Args:
            session: AsyncSession instance
            name: The name of the example
            description: Optional description
            price: Optional price
            is_active: Whether the item is active

        Returns:
            The newly created Example instance
        """
        example = cls(
            name=name,
            description=description,
            price=price,
            is_active=is_active
        )
        session.add(example)
        await session.flush()  # Get the ID
        await session.refresh(example)
        _logger.info("example_created", example_id=example.id, name=name)
        return example

    # ==================== UPDATE OPERATIONS ====================

    async def update(self, session: AsyncSession, **kwargs: Any) -> "Example":
        """
        Update the current Example record with given values.

        Args:
            session: AsyncSession instance
            **kwargs: Fields to update (name, description, price, is_active)

        Returns:
            The updated Example instance
        """
        allowed_fields = {'name', 'description', 'price', 'is_active'}
        for key, value in kwargs.items():
            if key in allowed_fields and value is not None:
                setattr(self, key, value)

        await session.flush()
        await session.refresh(self)
        _logger.info("example_updated", example_id=self.id)
        return self

    # ==================== DELETE OPERATIONS ====================

    @classmethod
    async def delete_by_id(cls, id_: int | str, session: AsyncSession) -> bool:
        """
        Delete a record by ID.

        Args:
            id_: The ID of the record to delete
            session: AsyncSession instance

        Returns:
            True if deleted, False if not found
        """
        result = await session.execute(
            delete(cls).where(cls.id == int(id_))
        )
        deleted = result.rowcount > 0
        if deleted:
            _logger.info("example_deleted", example_id=id_)
        return deleted

    async def delete(self, session: AsyncSession) -> None:
        """
        Delete the current instance.

        Args:
            session: AsyncSession instance
        """
        await session.delete(self)
        _logger.info("example_deleted", example_id=self.id)

    # ==================== SERIALIZATION ====================

    @property
    def serialized(self) -> dict[str, Any]:
        """Serialize the model to a dictionary."""
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "description": self.description,
            "price": float(self.price) if self.price is not None else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
