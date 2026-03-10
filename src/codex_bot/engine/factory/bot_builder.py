"""
BotBuilder — Builder pattern for creating Bot + Dispatcher.

Allows explicit control over the order of middleware connection.
"""

from __future__ import annotations

import logging
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage

log = logging.getLogger(__name__)


class BotBuilder:
    """Builder for Bot + Dispatcher with explicit middleware management.

    Allows injecting custom middleware at arbitrary points,
    unlike the functional approach with a fixed order.

    Args:
        bot_token: Telegram bot token.
        parse_mode: Message parsing mode (default is ``"HTML"``).
        fsm_storage: FSM storage. ``None`` → ``MemoryStorage``.
        dispatcher_kwargs: Additional kwargs for ``Dispatcher``.

    Raises:
        ValueError: If ``bot_token`` is empty.

    Example:
        ```python
        from codex_bot.engine.factory import BotBuilder
        from codex_bot.engine.middlewares import UserValidationMiddleware, ThrottlingMiddleware

        builder = BotBuilder(bot_token=settings.bot_token, fsm_storage=RedisStorage(redis))
        builder.add_middleware(UserValidationMiddleware())
        builder.add_middleware(ThrottlingMiddleware(redis=redis_client))
        builder.add_middleware(MyAnalyticsMiddleware())
        bot, dp = builder.build()
        ```
    """

    def __init__(
        self,
        bot_token: str,
        parse_mode: str = "HTML",
        fsm_storage: BaseStorage | None = None,
        dispatcher_kwargs: dict[str, Any] | None = None,
    ) -> None:
        if not bot_token:
            raise ValueError("bot_token must not be empty")

        self._bot_token = bot_token
        self._parse_mode = parse_mode
        self._fsm_storage: BaseStorage = fsm_storage or MemoryStorage()
        self._dispatcher_kwargs: dict[str, Any] = dispatcher_kwargs or {}
        self._middlewares: list[Any] = []

    def add_middleware(self, middleware: Any) -> BotBuilder:
        """Adds middleware to the connection queue.

        Middleware are connected in the order they are added.

        Args:
            middleware: Middleware instance to connect to ``dp.update``.

        Returns:
            ``self`` for chaining.

        Example:
            ```python
            builder.add_middleware(UserValidationMiddleware())
                   .add_middleware(ThrottlingMiddleware(redis))
            ```
        """
        self._middlewares.append(middleware)
        return self

    def build(self) -> tuple[Bot, Dispatcher]:
        """Assembles Bot and Dispatcher.

        Creates a ``Bot`` with the specified parameters and a ``Dispatcher`` with FSM storage.
        Connects all middleware via ``dp.update.middleware``.

        Returns:
            Tuple ``(bot, dispatcher)``.

        Example:
            ```python
            bot, dp = builder.build()
            await dp.start_polling(bot)
            ```
        """
        bot = Bot(
            token=self._bot_token,
            default=DefaultBotProperties(parse_mode=self._parse_mode),
        )

        dp = Dispatcher(storage=self._fsm_storage, **self._dispatcher_kwargs)

        for middleware in self._middlewares:
            dp.update.middleware(middleware)
            log.debug(f"BotBuilder | Middleware registered: {middleware.__class__.__name__}")

        log.info(f"BotBuilder | Built bot with {len(self._middlewares)} middleware(s)")
        return bot, dp
