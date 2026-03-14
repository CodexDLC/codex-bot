"""
Director — Request-scoped coordinator for cross-feature navigation.

The Director oversees transitions between independent feature modules by managing
FSM state changes and orchestrator resolution. It acts as a bridge between the
DI container and the business logic of individual features, ensuring that
orchestrators remain stateless and decoupled from session management.
"""

from __future__ import annotations

import logging
from typing import Any

from aiogram.fsm.context import FSMContext

from ..base.view_dto import UnifiedViewDTO
from .protocols import ContainerProtocol, OrchestratorProtocol

log = logging.getLogger(__name__)


class Director:
    """Coordinator of transitions between features (scenes).

    The Director is instantiated per incoming request (request-scoped) to capture
    ephemeral context such as user ID, chat ID, and the current FSM state. It facilitates
    the "Stateful Navigation, Stateless Logic" pattern by providing this context
    to singletons of `OrchestratorProtocol`.

    Attributes:
        REDIRECT_KEY: Primary metadata key for-driven navigation.
        LEGACY_REDIRECT_KEY: Deprecated navigation key for backward compatibility.

    Example:
        ```python
        director = Director(
            container=container,
            state=state,
            user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
        )
        view = await director.set_scene(feature="booking", payload={"id": 1})
        ```
    """

    # System keys for metadata-driven navigation
    REDIRECT_KEY = "__next_scene__"
    LEGACY_REDIRECT_KEY = "next_scene"

    def __init__(
        self,
        container: ContainerProtocol,
        state: FSMContext | None = None,
        user_id: int | None = None,
        chat_id: int | None = None,
        trigger_id: int | None = None,
    ) -> None:
        self.container = container
        self.state = state
        self.user_id = user_id
        self.chat_id = chat_id
        self.trigger_id = trigger_id

    async def resolve(self, data: Any) -> UnifiedViewDTO | Any:
        """Analyze incoming data for navigation instructions and resolve redirects.

        Performs a deep inspection of the provided data envelope to detect
        navigation metadata. If a redirect key is present, it automatically
        invokes `set_scene`.

        Args:
            data: Incoming request payload or response from a downstream service.
                Expected to be a dictionary containing 'meta' or 'payload' keys,
                or a flat dictionary structure.

        Returns:
            A `UnifiedViewDTO` if a redirect was successfully resolved,
            otherwise returns the original business payload (unwrapped).

        Raises:
            RuntimeError: If the resolved orchestrator fails to process the payload.
        """
        if not isinstance(data, dict):
            return data

        # 1. Detect Navigation (Metadata or Key)
        meta = data.get("meta", {}) if "meta" in data else data
        next_feature = meta.get(self.REDIRECT_KEY) or meta.get(self.LEGACY_REDIRECT_KEY)

        # 2. Extract Business Payload
        payload = data.get("payload") if "payload" in data else data

        # 3. Handle redirect if instructed by backend/data
        if next_feature:
            log.info(f"Director | Smart Resolve: Redirecting to '{next_feature}'")

            # Clean up all possible navigation keys from payload copy if it's a flat dict
            if isinstance(payload, dict):
                has_nav_keys = self.REDIRECT_KEY in payload or self.LEGACY_REDIRECT_KEY in payload
                if has_nav_keys:
                    payload = payload.copy()
                    payload.pop(self.REDIRECT_KEY, None)
                    payload.pop(self.LEGACY_REDIRECT_KEY, None)

            return await self.set_scene(feature=next_feature, payload=payload)

        return payload

    async def set_scene(self, feature: str, payload: Any = None) -> UnifiedViewDTO | Any:
        """Execute a cross-feature transition and invoke the target orchestrator.

        Performs atomic state synchronization and logic hand-off. The method
        retrieves the requested orchestrator from the DI container, updates
        the user's FSM state (if required), and executes the entry logic.

        Args:
            feature: Unique identifier of the target feature in the DI container.
            payload: Ephemeral data to pass to the feature's entry point.

        Returns:
            An instance of `UnifiedViewDTO` enriched with session metadata for
            immediate rendering.

        Side Effects:
            - Updates the FSM state via `self.state.set_state()`.
            - Logs navigation events for auditability.
        """
        orchestrator = self.container.features.get(feature)

        if orchestrator is None:
            log.error(f"Director | unknown_feature='{feature}' user_id={self.user_id}")
            return None

        # 1. Idempotent FSM state change
        expected_state = getattr(orchestrator, "expected_state", None)
        if self.state and expected_state:
            current_state = await self.state.get_state()
            if current_state != expected_state:
                await self.state.set_state(expected_state)
                log.debug(f"Director | State changed: {current_state} -> {expected_state}")

        # 2. Call orchestrator (Strict Protocol Check with Keyword Arguments)
        if isinstance(orchestrator, OrchestratorProtocol):
            view = await orchestrator.handle_entry(director=self, payload=payload)
        else:
            log.warning(f"Director | '{feature}' does not implement OrchestratorProtocol")
            return None

        # 3. Fallback enrichment of UnifiedViewDTO with session data
        if isinstance(view, UnifiedViewDTO):
            view = view.model_copy(
                update={
                    "chat_id": view.chat_id or self.chat_id,
                    "session_key": view.session_key or self.user_id,
                    "trigger_message_id": view.trigger_message_id or self.trigger_id,
                }
            )

        return view
