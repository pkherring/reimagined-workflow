"""Connection strings and settings for the database."""
from os import environ as env

from sqlalchemy.engine.url import URL
from sqlalchemy.orm import DeclarativeBase

url_object = URL.create(
    "postgresql+psycopg2",
    username="postgres",
    password="postgres",  # plain (unescaped) text
    host="localhost",
    database="reimagined-octo-goggles",
)

class Base(DeclarativeBase):
    """Base class for sqlalchemy models."""
    __abstract__ = True

    def __repr__(self):
        """Return a string representation of the model."""
        return f"<{self.__class__.__name__} {self.id}>"


