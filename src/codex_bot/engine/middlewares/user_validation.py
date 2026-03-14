"""
RBAC Orchestrator — Unified user validation and security context.

Extracts user identity from polymorphic Telegram events and facilitates
Role-Based Access Control (RBAC) by injecting authorization metadata
into the request context. Prepares user-scoped data for business logic.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from ..protocols import ContainerProtocol

log = logging.getLogger(__name__)


class UserValidationMiddleware(BaseMiddleware):
    """Middleware for validating users and injecting RBAC data.

    Key features:
    - **Universal**: Supports all update types via 'event_from_user'.
    - **RBAC**: Injects ``is_admin`` flag using ContainerProtocol.
    - **Safe**: Handles events without an associated user.

    Args:
        container: Object implementing ContainerProtocol for admin checks.
    """

    def __init__(self, container: ContainerProtocol) -> None:
        self.container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Processes the incoming event."""
        # aiogram 3.x automatically extracts the user into 'event_from_user'
        user: User | None = data.get("event_from_user")

        if user:
            data["user"] = user
            data["is_admin"] = self.container.is_admin(user.id)
            log.debug(f"UserValidation | user_id={user.id} is_admin={data['is_admin']}")
        else:
            data["is_admin"] = False
            log.debug("UserValidation | No user found in event")

        return await handler(event, data)
