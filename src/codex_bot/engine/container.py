"""
BaseBotContainer — Core DI container for all codex-bot projects.
Provides shared services and lifecycle management.
"""

import asyncio
import logging
from typing import Any, Protocol

from aiogram import Bot

from codex_bot.sender.sender_manager import SenderManager
from codex_bot.sender.view_sender import ViewSender

log = logging.getLogger(__name__)


class SettingsProtocol(Protocol):
    """Ensures settings have required admin lists."""

    @property
    def superuser_ids_list(self) -> list[int]: ...
    @property
    def owner_ids_list(self) -> list[int]: ...


class BaseBotContainer:
    """
    Abstract Base Container.

    Responsibilities:
    - Managing Bot and ViewSender instances.
    - Centralized RBAC (is_admin).
    - Orchestrator registry access.
    """

    def __init__(self, settings: Any, redis_client: Any | None = None):
        self.settings = settings
        self.redis_client = redis_client
        self._bot: Bot | None = None
        self._view_sender: ViewSender | None = None
        self.features: dict[str, Any] = {}

    @property
    def bot(self) -> Bot:
        """Access the bot instance with safety check."""
        if not self._bot:
            raise RuntimeError("Bot instance has not been initialized in the Container!")
        return self._bot

    @property
    def view_sender(self) -> ViewSender:
        """Access the view sender with safety check."""
        if not self._view_sender:
            raise RuntimeError("ViewSender has not been initialized. Call set_bot() first.")
        return self._view_sender

    def get_feature(self, key: str) -> Any:
        """Retrieve a specific feature orchestrator."""
        feature = self.features.get(key)
        if not feature:
            raise KeyError(f"Feature '{key}' is not registered or discovered.")
        return feature

    def is_admin(self, user_id: int) -> bool:
        """Centralized RBAC check (Owners/Superusers)."""
        is_owner = user_id in getattr(self.settings, "owner_ids_list", [])
        is_superuser = user_id in getattr(self.settings, "superuser_ids_list", [])
        return is_owner or is_superuser

    def set_bot(self, bot: Bot) -> None:
        """Configures services that require a bot instance."""
        self._bot = bot
        # Initialize the manager for UI message tracking
        # Mypy: ignore arg-type because storage can be Any | None in this context
        manager = SenderManager(storage=self.redis_client)  # type: ignore[arg-type]
        self._view_sender = ViewSender(bot=bot, manager=manager)

    async def shutdown(self) -> None:
        """Base shutdown logic for features."""
        log.info("Starting container shutdown...")
        cleanup_tasks = []

        for _, feature in self.features.items():
            if hasattr(feature, "shutdown") and callable(feature.shutdown):
                cleanup_tasks.append(feature.shutdown())
            elif hasattr(feature, "close") and callable(feature.close):
                cleanup_tasks.append(feature.close())

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        log.info("Base container shutdown completed.")
