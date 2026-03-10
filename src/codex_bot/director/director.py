"""
Director — Coordinator of cross-feature transitions.

The Director knows how to transition from one feature to another: change the FSM state,
get the required orchestrator from the container, and call its handle_entry().
Orchestrators are stateless — the Director passes itself as context with each call.
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

    Instantiated in the handler for each incoming request.
    Stores the request context (user_id, chat_id, state) and passes itself
    to orchestrators as an argument — no mutable state in the orchestrator.

    Args:
        container: Project's DI container with a ``features`` attribute.
        state: FSM context of the current user.
        user_id: Telegram ID of the user.
        chat_id: Target chat ID.
        trigger_id: ID of the trigger message (e.g., /start) for subsequent deletion.

    Example:
        ```python
        director = Director(
            container=container,
            state=state,
            user_id=callback.from_user.id,
            chat_id=callback.message.chat.id,
        )
        view = await director.set_scene(feature="booking", payload=None)
        await sender.send(view)
        ```
    """

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

    async def set_scene(self, feature: str, payload: Any = None) -> Any:
        """Cross-feature transition: changes FSM state and calls the feature orchestrator.

        Algorithm:
        1. Retrieves the orchestrator by key from ``container.features``.
        2. Sets the FSM state if the orchestrator has declared it.
        3. Passes itself to ``handle_entry(director=self, payload=payload)``.
        4. Enriches the result with ``chat_id`` and ``session_key`` as a fallback.

        Args:
            feature: Orchestrator key in ``container.features`` (e.g., ``"booking"``).
            payload: Data to pass to ``handle_entry()``.

        Returns:
            UnifiedViewDTO or any orchestrator result. None if the feature is not found.
        """
        orchestrator = self.container.features.get(feature)

        if orchestrator is None:
            log.error(f"Director | unknown_feature='{feature}' user_id={self.user_id}")
            return None

        # 1. FSM state change
        if self.state and hasattr(orchestrator, "expected_state") and orchestrator.expected_state:
            await self.state.set_state(orchestrator.expected_state)

        # 2. Call handle_entry (pass self as context) or render
        if isinstance(orchestrator, OrchestratorProtocol):
            view = await orchestrator.handle_entry(director=self, payload=payload)
        elif hasattr(orchestrator, "render"):
            view = await orchestrator.render(payload, self)
        else:
            log.warning(f"Director | orchestrator='{feature}' has no handle_entry or render")
            return None

        # 3. Fallback enrichment of UnifiedViewDTO with session data
        if isinstance(view, UnifiedViewDTO):
            view = view.model_copy(
                update={
                    "chat_id": view.chat_id or self.chat_id,
                    "session_key": view.session_key or self.user_id,
                }
            )

        return view
