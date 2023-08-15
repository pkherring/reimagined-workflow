"Test models."
from collections.abc import Generator
from sqlalchemy import Engine, create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker
import pytest

from src.db.models import (
    Users,
    Groups,
    Posts,
)

from src.db.connector import Base


@pytest.fixture(scope="module")
def test_engine() -> Engine:
    """Create connection engine to the database for testing. This is only used for testing.

    Returns
    -------
        Engine: Connection to database
    """
    url_object = URL.create(
        "postgresql+psycopg2",
        username="postgres",
        password="postgres",  # plain (unescaped) text
        host="localhost",
        database="reimagined-octo-goggles",
    )
    return create_engine(url_object)


@pytest.fixture(scope="module")
def init_db(test_engine: Engine) -> Generator[None, None, None]:
    """Create connection engine to the database for testing. This is only used for testing.

    Returns
    -------
        Generator: yield database
    """
    Base.metadata.drop_all(test_engine)
    Base.metadata.create_all(test_engine)
    yield None

def test_users_model(init_db: None, test_engine: Engine):
    """Test the Users model."""
    Session = sessionmaker(bind=test_engine)
    with Session() as session:
        user1 = Users(
            name="John Doe",
            email="john@you.com",
            password="password",
        )
        session.add(user1)
        user2 = Users(
            name="Jane Doe",
            email="jane@you.com",
            password="password",
        )
        session.add(user2)
        group = Groups(
            name="Group1",
            domain="you.com",
        )
        session.add(group)
        session.commit()

    with Session() as session:
        post1 = Posts(
            title="Post1",
            content="Content1",
            author=user1,
            group=group,
        )
        session.add(post1)
        post2 = Posts(
            title="Post2",
            content="Content2",
            author=user2,
            group=group,
        )   
        session.add(post2)
        session.commit()

    with Session() as session:
        get_user = session.query(Users).filter_by(name="John Doe").first()
        if get_user:
            assert get_user.name == "John Doe"
            assert get_user.email == "john@you.com"
        else:
            raise AssertionError("User not found")
