import asyncio

from example_web_app.config import db_option
from example_web_app.database import db, transactional_session
from example_web_app.models.example import Example
from example_web_app.logger import get_logger


_logger = get_logger()


def init_example():
    _logger.info("[Init-Example] creating new database engine")
    db.initialize()

    # Check if the table exist
    if not db.engine.dialect.has_table(db.engine, Example.__tablename__, db_option('schema')):
        _logger.info("[Init-Example] creating new database table: `example`")
        Example.__table__.create(bind=db.engine)

    _logger.info("[Init-Example] creating new rows in table: `example`")
    async def create_new_examples():
        async with transactional_session() as session:
            for i in range(1, 5):
                session.add(Example(name=f"Example #{i}"))
                session.commit()

    asyncio.get_event_loop().run_until_complete(create_new_examples())

    _logger.info("[Init-Example] cleaning up the database engine resources")
    db.cleanup()

    _logger.info("[Init-Example] done...")


if __name__ == '__main__':
    init_example()

