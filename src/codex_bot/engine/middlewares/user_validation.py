"""
UserValidationMiddleware — User presence check in an event.

Blocks processing of events without from_user (protection against system events,
channels without a subscriber, bots). Adds user to data for handlers.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

log = logging.getLogger(__name__)


class UserValidationMiddleware(BaseMiddleware):
    """
    User validation middleware in an incoming event.

    For Message and CallbackQuery:
    - Blocks events without from_user (returns None).
    - Adds `data["user"]` — an aiogram User object — for handlers.

    For other event types (Update, etc.) — passes without checking,
    allowing the bot to send messages to channels.

    Example:
        ```python
        dp.message.middleware(UserValidationMiddleware())
        dp.callback_query.middleware(UserValidationMiddleware())
        ```
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if isinstance(event, Message | CallbackQuery):
            user = event.from_user
            if not user:
                log.warning(f"UserValidation | no from_user event_type={type(event).__name__}")
                return None
            data["user"] = user

        return await handler(event, data)
