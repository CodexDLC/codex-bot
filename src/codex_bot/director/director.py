"""
Director — Request-scoped coordinator for cross-feature navigation.

The Director oversees transitions between independent feature modules by managing
FSM state changes and orchestrator resolution. It acts as a bridge between the
DI container and the business logic of individual features, ensuring that
orchestrators remain stateless and decoupled from session management.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from aiogram.fsm.context import FSMContext

from ..base.view_dto import UnifiedViewDTO
from .protocols import ContainerProtocol

if TYPE_CHECKING:
    pass

log = logging.getLogger(__name__)


class Director:
    """Coordinator of transitions between features (scenes).

    The Director is instantiated per incoming request (request-scoped) to capture
    abstract session and context identifiers. It facilitates the
    "Stateful Navigation, Stateless Logic" pattern.

    Attributes:
        REDIRECT_KEY: Primary metadata key for-driven navigation.
        MAX_REDIRECTS: Maximum number of allowed redirects (loop prevention).
    """

    REDIRECT_KEY = "__next_scene__"
    MAX_REDIRECTS: int = 5

    def __init__(
        self,
        container: ContainerProtocol,
        state: FSMContext | None = None,
        session_key: int | str | None = None,
        context_id: int | str | None = None,
        trigger_id: int | None = None,
    ) -> None:
        self.container = container
        self.state = state
        self.session_key = session_key
        self.context_id = context_id
        self.trigger_id = trigger_id

        self._redirect_count: int = 0

    async def resolve(self, data: Any) -> UnifiedViewDTO | Any:
        """Analyze incoming data for navigation instructions and resolve redirects.

        Args:
            data: Incoming request payload.

        Returns:
            A `UnifiedViewDTO` if a redirect was resolved, else business payload.
        """
        # Recursion protection
        if self._redirect_count >= self.MAX_REDIRECTS:
            log.error("Director | Loop detected in resolve transitions")
            return data

        # Safe parsing: Only dicts contain metadata for transitions
        if not isinstance(data, dict):
            return data

        # 1. Detect Navigation inside meta envelope
        meta = data.get("meta", {})
        if not isinstance(meta, dict):
            # Fallback if meta is not a dict
            return data

        next_feature = meta.get(self.REDIRECT_KEY)

        # 2. Extract Business Payload
        # If 'payload' key exists, it's the payload, otherwise it's the whole dict
        payload = data.get("payload", data)

        # 3. Handle redirect
        if next_feature and isinstance(next_feature, str):
            log.info(f"Director | Smart Resolve: Redirecting to '{next_feature}'")
            return await self.set_scene(feature=next_feature, payload=payload)

        return payload

    async def set_scene(self, feature: str, payload: Any = None) -> UnifiedViewDTO | Any:
        """Execute a cross-feature transition with Guard checks and Auto-Wrapping.

        Args:
            feature: Identifier of the target feature.
            payload: Ephemeral data for the transition.
        """
        # 0. Safety Invariants
        self._redirect_count += 1
        if self._redirect_count > self.MAX_REDIRECTS:
            log.error(f"Director | Redirect limit reached at '{feature}'")
            return UnifiedViewDTO(alert_text="Ошибка навигации: обнаружен цикл")

        orchestrator = self.container.features.get(feature)
        if orchestrator is None:
            log.error(f"Director | Unknown feature='{feature}'")
            return None

        # 1. Transition Guards (OCP Integration)
        for guard in self.container.transition_guards:
            result = await guard.check_access(self, feature=feature, orchestrator=orchestrator, payload=payload)
            if isinstance(result, UnifiedViewDTO):
                log.warning(f"Director | Guard {guard.__class__.__name__} blocked {feature}")
                return result

        # 2. Atomic FSM State Change
        expected_state = getattr(orchestrator, "expected_state", None)
        if self.state and expected_state:
            await self.state.set_state(expected_state)

        # 3. Handle Entry
        view = await orchestrator.handle_entry(director=self, payload=payload)

        # 4. Auto-Wrapping and Enrichment
        if not isinstance(view, UnifiedViewDTO):
            # If orchestrator returned a ViewResultDTO or raw content
            view = UnifiedViewDTO(content=view)

        # 5. Domain-Agnostic Session Enrichment
        view = view.model_copy(
            update={
                "chat_id": view.chat_id or self.context_id,
                "session_key": view.session_key or self.session_key,
                "trigger_message_id": view.trigger_message_id or self.trigger_id,
            }
        )

        return view
