"""
Declarative Foundation — Core SQLAlchemy schema definitions.

Establishes the base classes and naming conventions for the framework's
object-relational mapping. Ensures deterministic constraint names across
different database dialects for reliable Alembic migration generation.
"""

from datetime import datetime

from sqlalchemy import BigInteger, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

# Naming convention for Alembic migrations
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all Bot SQLAlchemy models."""

    metadata = MetaData(naming_convention=convention)


class TimestampMixin:
    """Mixin to add created_at and updated_at columns."""

    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now(), nullable=False)


class IDMixin:
    """Mixin to add a standard primary key ID column."""

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)


class BaseModel(Base, IDMixin, TimestampMixin):
    """
    All-in-one base model for project entities.
    Inherits ID and Timestamps automatically.
    """

    __abstract__ = True
