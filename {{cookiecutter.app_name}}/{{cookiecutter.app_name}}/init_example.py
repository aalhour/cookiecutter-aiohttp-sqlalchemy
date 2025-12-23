"""
Example initialization script for populating the database with sample data.

This script demonstrates how to:
- Initialize the database connection
- Create sample records using the async ORM
- Can be run via: python -m {{cookiecutter.app_name}}.init_example
"""
import asyncio
from decimal import Decimal

from {{cookiecutter.app_name}}.database import db, transactional_session
from {{cookiecutter.app_name}}.logger import get_logger
from {{cookiecutter.app_name}}.models.example import Example

_logger = get_logger()


# Sample data to seed the database
SAMPLE_EXAMPLES = [
    {
        "name": "Premium Widget",
        "description": "A high-quality widget for all your needs",
        "price": Decimal("49.99"),
        "is_active": True,
    },
    {
        "name": "Basic Gadget",
        "description": "An affordable gadget for everyday use",
        "price": Decimal("19.99"),
        "is_active": True,
    },
    {
        "name": "Deluxe Thingamajig",
        "description": "The ultimate thingamajig with all the bells and whistles",
        "price": Decimal("99.99"),
        "is_active": True,
    },
    {
        "name": "Discontinued Doohickey",
        "description": "This product has been discontinued",
        "price": Decimal("9.99"),
        "is_active": False,
    },
]


async def seed_data() -> None:
    """Insert sample data into the database."""
    async with transactional_session() as session:
        for item_data in SAMPLE_EXAMPLES:
            example = await Example.create(
                session=session,
                name=item_data["name"],
                description=item_data["description"],
                price=float(item_data["price"]),
                is_active=item_data["is_active"],
            )
            _logger.info(
                "created_sample_example",
                example_id=example.id,
                name=example.name
            )

    _logger.info("seed_complete", count=len(SAMPLE_EXAMPLES))


async def async_init_example() -> None:
    """Async initialization of example data."""
    _logger.info("init_example_start")

    # Initialize the database
    db.initialize()

    try:
        # Check if data already exists
        async with transactional_session() as session:
            existing = await Example.get_all(session)
            if existing:
                _logger.info(
                    "init_example_skip",
                    reason="Data already exists",
                    count=len(existing)
                )
                return

        # Seed the data
        await seed_data()
        _logger.info("init_example_complete")

    finally:
        await db.cleanup()


def init_example() -> None:
    """Entry point for the init_example console script."""
    asyncio.run(async_init_example())


if __name__ == '__main__':
    init_example()
