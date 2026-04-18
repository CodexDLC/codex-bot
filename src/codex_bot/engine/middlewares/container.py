"""
DI Orchestration — Centralized service injection middleware.

Facilitates dependency injection by propagating the framework's DI container
into the Aiogram request context. Ensures all downstream middlewares and
handlers have consistent access to shared services and infrastructure.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from ..protocols import ContainerProtocol

log = logging.getLogger(__name__)


class ContainerMiddleware(BaseMiddleware):
    """Middleware for injecting the Dependency Injection container.

    Args:
        container: Object implementing ContainerProtocol.
    """

    def __init__(self, container: ContainerProtocol) -> None:
        self.container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        """Injects the container into the context data."""
        data["container"] = self.container
        return await handler(event, data)
