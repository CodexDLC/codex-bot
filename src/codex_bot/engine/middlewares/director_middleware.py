"""
Context Coordinator — Automatic Director instantiation for framework navigation.

Orchestrates the lifecycle of the `Director` instance for each incoming
update. Normalizes event context and ensures handlers receive a fully
configured request-scoped coordinator with access to state and DI services.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

from ...director.director import Director
from ...helper.context_helper import ContextHelper

log = logging.getLogger(__name__)


class DirectorMiddleware(BaseMiddleware):
    """
    Middleware that injects a `Director` instance into the handler data.

    Uses 'ContextHelper' to normalize IDs from different event types.
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

        # 2. Extract unified context using Helper
        ctx = ContextHelper.extract_base_context(event)

        # 3. Instantiate Director
        director = Director(
            container=container, state=state, user_id=ctx.user_id, chat_id=ctx.chat_id, trigger_id=ctx.message_id
        )

        # 4. Inject into data for handlers
        data["director"] = director

        return await handler(event, data)
