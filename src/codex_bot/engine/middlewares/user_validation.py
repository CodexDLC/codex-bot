"""
UserValidationMiddleware — Unified user and permission management.

Retrieves user from events and performs authorization via the BotContainer.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

log = logging.getLogger(__name__)


class ContainerProtocol(Protocol):
    """Protocol to ensure the container has required RBAC methods."""

    def is_admin(self, user_id: int) -> bool: ...


class UserValidationMiddleware(BaseMiddleware):
    """
    Middleware for user validation and centralized RBAC.

    Injects into 'data':
    - `user`: aiogram.types.User
    - `is_admin`: bool (delegated to container.is_admin)
    """

    def __init__(self, container: ContainerProtocol):
        """
        Initializes the middleware with a DI container.

        Args:
            container: The BotContainer instance.
        """
        self.container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message | CallbackQuery):
            user = event.from_user
            if not user:
                log.debug(f"UserValidation | No user in event {type(event).__name__}")
                return None

            user_id = user.id
            data["user"] = user

            # Delegate RBAC check to the container
            # This allows for dynamic roles (DB, Cache, etc.) without changing middleware
            data["is_admin"] = self.container.is_admin(user_id)

        return await handler(event, data)
