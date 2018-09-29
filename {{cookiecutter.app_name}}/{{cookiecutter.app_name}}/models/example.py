import datetime
from typing import List

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import INTEGER, TIMESTAMP, TEXT
from sqlalchemy.orm import Session

from {{cookiecutter.app_name}}.database import db
from {{cookiecutter.app_name}}.background import run_async
from {{cookiecutter.app_name}}.logger import get_logger


__all__ = [
    "Example",
]


_logger = get_logger()


class Example(db.BaseModel):
    """
    Data model for Example DB table.
    """
    __tablename__ = 'example'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    name = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False), nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=False), nullable=True, onupdate=datetime.datetime.utcnow)

    def __init__(self, name):
        """
        New model instance initializer
        :param name: the name of the example
        """
        self.name = name

    @classmethod
    async def get_by_id(cls, id_: str, session: Session) -> "Example":
        """
        Returns a record by ID

        :param id_: stringified UUID, i.e.: str(uuid_object)
        :param session: SQLAlchemy database session
        :return: THe specified Example by id or None
        """
        ###
        # Run the SQLAlchemy session.query(Example).get() function in the background
        #
        return await run_async(session.query(cls).get, (id_,))

    @classmethod
    async def get_all(cls, session: Session) -> List["Example"]:
        """
        Returns all records in the table

        :param session: SQLAlchemy database session
        :return: List of all examples in the database
        """
        ###
        # Run the SQLAlchemy session.query(Example).get() function in the background
        #
        return await run_async(session.query(cls).all)

    @property
    def serialized(self):
        return {
            "id": str(self.id) if self.id else None,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

