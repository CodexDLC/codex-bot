"""
Transaction Management — Optimized SQLAlchemy session orchestration.

Implements the 'Session-per-Event' pattern for asynchronous database
interactions. Manages the lifecycle of SQLAlchemy sessions, providing
automatic commit on success and deterministic rollback on failure.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

log = logging.getLogger(__name__)


class DatabaseTransactionMiddleware(BaseMiddleware):
    """
    Middleware for managing the lifecycle of an async database session.

    Injects `data["db_session"]` into the handler context.
    """

    def __init__(self, session_maker: async_sessionmaker[AsyncSession]):
        """
        Args:
            session_maker: SQLAlchemy async_sessionmaker instance.
        """
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Start a new session for the current event context
        async with self.session_maker() as session:
            # Add session to data so it's accessible in handlers and other middlewares
            data["db_session"] = session

            try:
                # Pass control to the handler
                result = await handler(event, data)

                # Success: Commit all changes made during the event
                await session.commit()
                return result

            except Exception as e:
                # Error: Rollback changes to keep DB consistent
                log.error(f"Transaction failed, rolling back: {e}")
                await session.rollback()
                # Re-raise the exception for the global error handler
                raise e
