"""
Generic Repository Abstraction — Standardized Data Access Pattern.

Implements the Repository pattern to decouple business logic from persistence
concerns. Optimized for 'Direct' database mode, utilizing centralized transaction
management via middleware.
"""

from collections.abc import Sequence
from typing import Any, Generic, Protocol, TypeVar, cast, runtime_checkable

from sqlalchemy import delete, select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession


@runtime_checkable
class Identifiable(Protocol):
    """Protocol for models that have an 'id' attribute."""

    id: Any


# Type variable for the SQLAlchemy model
ModelType = TypeVar("ModelType", bound=Identifiable)


class BaseRepository(Generic[ModelType]):
    """
    Abstract Base Repository for CRUD operations.

    Inherit from this class and provide the model type.
    Note: Does not perform commits. Use DatabaseTransactionMiddleware.
    """

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """
        Initializes the repository with a specific model and session.

        Args:
            model: The SQLAlchemy model class.
            session: The async database session (usually from middleware).
        """
        self.model = model
        self.session = session

    async def get(self, pk: Any) -> ModelType | None:
        """Fetch a single record by primary key."""
        result = await self.session.get(self.model, pk)
        return result

    async def get_multi(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Fetch multiple records with pagination."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create(self, **kwargs: Any) -> ModelType:
        """Create and add a new record to the session."""
        obj = self.model(**kwargs)
        self.session.add(obj)
        # We don't commit here. Middleware will handle it.
        return obj

    async def update(self, pk: Any, **kwargs: Any) -> ModelType | None:
        """Update an existing record by primary key."""
        id_column = self.model.id
        query = update(self.model).where(id_column == pk).values(**kwargs).returning(self.model)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def remove(self, pk: Any) -> bool:
        """Delete a record by primary key."""
        id_column = self.model.id
        query = delete(self.model).where(id_column == pk)
        result = await self.session.execute(query)
        # Cast result to CursorResult[Any] to satisfy Mypy for rowcount
        cursor_result = cast(CursorResult[Any], result)
        row_count = cursor_result.rowcount or 0
        return bool(row_count > 0)
