"""Module for sqlalchemy models."""

from sqlalchemy import ForeignKey, Identity, Text, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from src.db.connector import Base

class Users(Base):
    """Model for users."""
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=False)
    email: Mapped[str] = mapped_column(Text, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    date_created: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    posts: Mapped[list["Posts"]] = relationship("Posts", back_populates="author")

class Groups(Base):
    """Model for products."""
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False, unique=False)
    domain: Mapped[str] = mapped_column(Text, unique=True)
    date_created: Mapped[str] = mapped_column(DateTime(timezone=True), nullable=False)
    posts: Mapped[list["Posts"]] = relationship("Posts", back_populates="group")

class Posts(Base):
    """Model for posts."""
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Identity(start=1), primary_key=True)
    title: Mapped[str] = mapped_column(Text, nullable=False, unique=False)
    content: Mapped[str] = mapped_column(Text, nullable=True, unique=False)
    caption: Mapped[str] = mapped_column(Text, nullable=True, unique=False)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"))
    author: Mapped["Users"] = relationship("Users", back_populates="posts")
    group: Mapped["Groups"] = relationship("Groups", back_populates="posts")