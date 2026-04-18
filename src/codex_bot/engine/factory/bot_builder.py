"""
Bot Orchestration Factory — Builder pattern for Bot and Dispatcher initialization.

Encapsulates the complex configuration of Aiogram components, enforcing correctly
ordered middleware registration (DI, Navigation, RBAC) and ensuring seamless
integration between the bot instance and the dependency injection container.
"""

from __future__ import annotations

import logging
from typing import Any

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage

from ..middlewares.container import ContainerMiddleware
from ..middlewares.director_middleware import DirectorMiddleware
from ..middlewares.user_validation import UserValidationMiddleware
from ..protocols import ContainerProtocol

log = logging.getLogger(__name__)


class BotBuilder:
    """Builder for Bot + Dispatcher with automatic core middleware management.

    Ensures that essential framework middlewares are registered in the correct sequence.
    Automatically injects the created ``Bot`` instance into the provided ``Container``.

    Args:
        bot_token: Telegram bot token obtained from @BotFather.
        parse_mode: Message parsing mode (default is ``"HTML"``).
        fsm_storage: FSM storage. ``None`` → ``MemoryStorage``.
        dispatcher_kwargs: Additional kwargs for ``Dispatcher`` initialization.

    Example:
        ```python
        builder = BotBuilder(bot_token="...")
        builder.setup_core(container=my_container)
        builder.add_project_middleware(MyAnalyticsMiddleware())

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
        """Initializes the builder with basic settings."""
        if not bot_token:
            raise ValueError("bot_token must not be empty")

        self._bot_token = bot_token
        self._parse_mode = parse_mode
        self._fsm_storage: BaseStorage = fsm_storage or MemoryStorage()
        self._dispatcher_kwargs: dict[str, Any] = dispatcher_kwargs or {}

        self._core_middlewares: list[BaseMiddleware] = []
        self._project_middlewares: list[BaseMiddleware] = []
        self._middlewares = self._project_middlewares  # Alias for backward compatibility in tests
        self._container: ContainerProtocol | None = None

    def setup_core(self, container: ContainerProtocol) -> BotBuilder:
        """Registers mandatory framework middlewares and links the container.

        Registration order:
        1. **Container Injection**: Makes the DI container available in context.
        2. **Director Initialization**: Creates the request coordinator.
        3. **User Validation (RBAC)**: Handles user identification and admin checks.

        Args:
            container: The project's DI container implementing ContainerProtocol.

        Returns:
            The builder instance for method chaining.
        """
        self._container = container

        # Internal core middleware setup
        self._core_middlewares = [
            ContainerMiddleware(container),
            DirectorMiddleware(),
            UserValidationMiddleware(container),
        ]
        return self

    def add_project_middleware(self, middleware: BaseMiddleware) -> BotBuilder:
        """Adds a project-specific middleware to the execution chain.

        Project middlewares are automatically registered AFTER the core framework ones.

        Args:
            middleware: Instance of an aiogram BaseMiddleware.

        Returns:
            The builder instance for method chaining.
        """
        self._project_middlewares.append(middleware)
        return self

    def add_middleware(self, middleware: BaseMiddleware) -> BotBuilder:
        """Alias for add_project_middleware. Maintained for backward compatibility."""
        return self.add_project_middleware(middleware)

    def build(self) -> tuple[Bot, Dispatcher]:
        """Assembles and configures Bot and Dispatcher.

        1. Creates the Bot instance.
        2. Injects the Bot into the Container (if linked via setup_core).
        3. Initializes the Dispatcher and registers all middlewares.

        Returns:
            A tuple of (Bot, Dispatcher).
        """
        bot = Bot(
            token=self._bot_token,
            default=DefaultBotProperties(parse_mode=self._parse_mode),
        )

        # Automatic Integration: Linking Bot and Container
        if self._container:
            self._container.set_bot(bot)
            log.debug("BotBuilder | Automatically injected Bot instance into Container")

        dp = Dispatcher(storage=self._fsm_storage, **self._dispatcher_kwargs)

        # Register Core Middlewares first (Outer level)
        for mw in self._core_middlewares:
            dp.update.outer_middleware(mw)
            log.debug(f"BotBuilder | Core Middleware: {mw.__class__.__name__}")

        # Register Project Middlewares
        for mw in self._project_middlewares:
            dp.update.outer_middleware(mw)
            log.debug(f"BotBuilder | Project Middleware: {mw.__class__.__name__}")

        log.info(
            f"BotBuilder | Built with {len(self._core_middlewares)} core "
            f"and {len(self._project_middlewares)} project middlewares"
        )
        return bot, dp
