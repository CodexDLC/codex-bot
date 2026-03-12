"""
DirectorMiddleware — Automatic Director instantiation for each event.

Ensures that every handler receives a ready-to-use 'director' object
in its arguments, pre-configured with the current state, container, and user IDs.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, TelegramObject

from ...director.director import Director

log = logging.getLogger(__name__)


class DirectorMiddleware(BaseMiddleware):
    """
    Middleware that injects a `Director` instance into the handler data.

    Depends on:
    - `ContainerMiddleware` (for `data["container"]`)
    - `state` (provided by aiogram Dispatcher/FSM)
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # 1. Extract required dependencies from context
        container = data.get("container")
        state: FSMContext | None = data.get("state")

        if not container:
            log.error("DirectorMiddleware | 'container' not found in data. Check middleware order!")
            return await handler(event, data)

        # 2. Extract IDs from event
        user_id = None
        chat_id = None
        trigger_id = None

        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
            chat_id = event.chat.id
            trigger_id = event.message_id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            chat_id = event.message.chat.id if event.message else None
            trigger_id = event.message.message_id if event.message else None

        # 3. Instantiate Director
        director = Director(container=container, state=state, user_id=user_id, chat_id=chat_id, trigger_id=trigger_id)

        # 4. Inject into data for handlers
        data["director"] = director

        return await handler(event, data)
