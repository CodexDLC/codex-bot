"""
BaseBotContainer — Core Dependency Injection (DI) container for the bot framework.

This module provides the central registry for system-wide services, including
the Bot instance, ViewSender, and feature orchestrators. It manages service
lifecycles and provides a centralized access point for cross-cutting concerns
like RBAC.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol, runtime_checkable

from aiogram import Bot

from codex_bot.sender.memory_storage import MemorySenderStorage
from codex_bot.sender.protocols import SenderStateStorageProtocol
from codex_bot.sender.redis_storage import RedisSenderStorage
from codex_bot.sender.sender_manager import SenderManager
from codex_bot.sender.view_sender import ViewSender

log = logging.getLogger(__name__)


class SettingsProtocol(Protocol):
    """Ensures settings have required admin lists."""

    superuser_ids_list: list[int]
    owner_ids_list: list[int]


@runtime_checkable
class FeatureProtocol(Protocol):
    """Contract for features that require graceful shutdown."""

    async def shutdown(self) -> None: ...


class BaseBotContainer:
    """Centralized registry for service orchestration and dependency management.

    The container acts as a mediator between infrastructure (Bot, Redis) and
    business logic (Orchestrators). It facilitates service discovery and
    provides a unified interface for system-wide operations.

    Responsibilities:
        - Decoupling infrastructure initialization from logic.
        - Managing service lifecycles (initialization and shutdown).
        - Providing centralized Role-Based Access Control (RBAC).

    Args:
        settings: An object complying with `SettingsProtocol` for configuration.
        redis_client: Optional asynchronous Redis client for persistence.
    """

    def __init__(self, settings: SettingsProtocol, redis_client: Any | None = None):
        self.settings = settings
        self.redis_client = redis_client
        self._bot: Bot | None = None
        self._view_sender: ViewSender | None = None
        # Registry of features: could be simple objects or complex orchestrators
        self.features: dict[str, FeatureProtocol | Any] = {}

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

    def get_feature(self, key: str) -> FeatureProtocol | Any:
        """Retrieve a specific feature orchestrator."""
        feature = self.features.get(key)
        if not feature:
            raise KeyError(f"Feature '{key}' is not registered or discovered.")
        return feature

    def is_admin(self, user_id: int) -> bool:
        """Centralized RBAC check (Owners/Superusers)."""
        is_owner = user_id in self.settings.owner_ids_list
        is_superuser = user_id in self.settings.superuser_ids_list
        return is_owner or is_superuser

    def set_bot(self, bot: Bot) -> None:
        """Configures services that require a bot instance.

        Automatically selects the coordinate storage type (Redis vs Memory)
        based on the availability of redis_client.
        """
        self._bot = bot

        # Smart storage selection for ViewSender coordinates
        storage: SenderStateStorageProtocol
        if self.redis_client:
            storage = RedisSenderStorage(self.redis_client)
            log.debug("Container | Using Redis for ViewSender coordinates")
        else:
            storage = MemorySenderStorage()
            log.warning("Container | Redis client missing. Using MemoryStorage for UI coordinates.")

        manager = SenderManager(storage=storage)
        self._view_sender = ViewSender(bot=bot, manager=manager)

    async def shutdown(self) -> None:
        """Execute a graceful shutdown for all registered features.

        Identifies all features complying with `FeatureProtocol` and invokes
        their shutdown handlers concurrently.

        Side Effects:
            - Closes database connections, file handles, or network sockets
              managed by individual features.
        """
        log.info("Starting container shutdown...")
        cleanup_tasks = []

        for name, feature in self.features.items():
            # Strict protocol check instead of duck typing (hasattr)
            if isinstance(feature, FeatureProtocol):
                log.debug(f"Container | Registering shutdown task for feature: {name}")
                cleanup_tasks.append(feature.shutdown())

        if cleanup_tasks:
            # return_exceptions=True ensures that one failing feature doesn't stop the rest
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)

        log.info("Base container shutdown completed.")
