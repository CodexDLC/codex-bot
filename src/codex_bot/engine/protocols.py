"""
Core Engine Protocols — Architectural contracts for framework infrastructure.

Defines the essential interfaces to ensure strict dependency inversion
across the bot's lifecycle. Provides type-safe abstractions for dependency
injection containers, system configuration, and service providers.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from aiogram import Bot


@runtime_checkable
class ContainerProtocol(Protocol):
    """Structural contract for the project's Dependency Injection (DI) Container.

    The container acts as the central registry for all system and business
    services, managing their lifecycles and providing controlled access to
    core infrastructure components.
    """

    def set_bot(self, bot: Bot) -> None:
        """Configures services requiring a Bot instance."""
        ...

    def is_admin(self, user_id: int) -> bool:
        """Centralized RBAC check."""
        ...

    async def shutdown(self) -> None:
        """Graceful shutdown of all services."""
        ...

    # Feature registry access
    features: dict[str, Any]
