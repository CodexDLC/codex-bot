"""
Protocols for Director — Dependency inversion without concrete classes.

OrchestratorProtocol describes the minimum contract of a stateless orchestrator,
ContainerProtocol — the minimum contract of the project's DI container.
The library does not know about specific implementations — only about interfaces.
"""

from typing import Any, NamedTuple, Protocol, runtime_checkable

from aiogram.fsm.state import State


class SceneConfig(NamedTuple):
    """Scene configuration: FSM state + entry-point service key.

    Used in the project's SCENE_ROUTES to describe cross-feature transitions.

    Attributes:
        fsm_state: Aiogram State set when entering the scene.
        entry_service: Orchestrator key in the container registry (e.g., ``"booking"``).

    Example:
        ```python
        SCENE_ROUTES = {
            "booking": SceneConfig(
                fsm_state=BookingStates.main,
                entry_service="booking",
            ),
        }
        ```
    """

    fsm_state: State
    entry_service: str


@runtime_checkable
class OrchestratorProtocol(Protocol):
    """Minimum contract for a stateless feature orchestrator.

    The Director works through this protocol without knowing about specific classes.
    BaseBotOrchestrator implements it automatically.

    The orchestrator must be stateless — it does not store user state.
    Context is passed via the ``director`` argument on each call.
    """

    async def render(self, payload: Any, director: Any) -> Any:
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
