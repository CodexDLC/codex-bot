"""
ContainerMiddleware — DI container injection into handlers.

Adds `data["container"]` so that handlers don't import the container
directly — they receive it from the event context.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class ContainerMiddleware(BaseMiddleware):
    """
    Middleware for injecting a DI container into handlers.

    Passes any container object via `data["container"]`.
    Does not know about the specific container type — works with any object.

    Args:
        container: Project's DI container (any object).

    Example:
        ```python
        container = BotContainer(settings=settings, redis=redis)
        dp.update.middleware(ContainerMiddleware(container=container))

        # In a handler:
        async def my_handler(callback: CallbackQuery, container: BotContainer):
            result = await container.booking_service.get_slots()
        ```
    """

    def __init__(self, container: Any) -> None:
        self.container = container

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["container"] = self.container
        return await handler(event, data)
