"""Module for sqlalchemy models."""

from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.db.connector import Base

class Users(Base):
    """Model for users."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    posts = relationship("Post", back_populates="author")

class Groups(Base):
    """Model for products."""
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    domain = Column(String, unique=True)
    posts = relationship("Post", back_populates="group")

class Posts(Base):
    """Model for posts."""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    author_id = Column(Integer, ForeignKey("users.id"))
    group_id = Column(Integer, ForeignKey("groups.id"))
    author = relationship("User", back_populates="posts")
    group = relationship("Group", back_populates="posts")