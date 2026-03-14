"""
Protocols for the Director — Interface definitions for dependency inversion.

This module defines the structural protocols required for the Director to
interact with features and the DI container without being coupled to
specific implementations.
"""

from typing import Any, NamedTuple, Protocol, runtime_checkable

from aiogram.fsm.state import State


class SceneConfig(NamedTuple):
    """Configuration schema for feature entry points.

    Defines the mapping between a logical feature key and its associated
    Telegram FSM state. Used to drive the orchestration logic in the Director.

    Attributes:
        fsm_state: The `aiogram` State object to activate upon entry.
        entry_service: The lookup key for the orchestrator in the DI registry.

    Example:
        ```python
        SCENE_ROUTES = {
            "main": SceneConfig(fsm_state=Menu.main, entry_service="main_menu")
        }
        ```
    """

    fsm_state: State
    entry_service: str


@runtime_checkable
class OrchestratorProtocol(Protocol):
    """Structural protocol for stateless feature orchestrators.

    Orchestrators complying with this protocol must be stateless singletons.
    They are responsible for transforming incoming payloads into UI responses
    using the provided `Director` context.
    """

    async def render(self, director: Any, payload: Any = None) -> Any:
        """Renders content for the passed payload."""
        ...

    async def handle_entry(
        self,
        director: Any,
        payload: Any = None,
    ) -> Any:
        """Entry point into the feature."""
        ...


@runtime_checkable
class ContainerProtocol(Protocol):
    """Minimum contract for the project's DI container.

    The Director only requires the ``features`` attribute — a dictionary of orchestrators.
    The specific BotContainer of the project must provide this attribute.

    Attributes:
        features: Dictionary of ``{feature_key: orchestrator}``.

    Example:
        ```python
        class BotContainer:
            def __init__(self):
                self.features: dict[str, Any] = {}
        ```
    """

    features: dict[str, OrchestratorProtocol]
