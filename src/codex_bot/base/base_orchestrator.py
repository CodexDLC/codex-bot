"""
BaseBotOrchestrator — Abstract STATELESS feature orchestrator.

The Orchestrator is the heart of each feature. It knows how to transform
an incoming payload into a UnifiedViewDTO for sending to the user.

IMPORTANT: The class must be Stateless — it does not store user state in self.
Orchestrators are singletons shared between all concurrent requests.
All context is passed through method arguments (director, payload).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from codex_bot.base.view_dto import UnifiedViewDTO, ViewResultDTO

if TYPE_CHECKING:
    from codex_bot.director.director import Director

PayloadT = TypeVar("PayloadT")
"""TypeVar for the orchestrator payload. A specific subclass specifies the type explicitly."""


class BaseBotOrchestrator(ABC, Generic[PayloadT]):  # noqa: UP046
    """Abstract STATELESS feature orchestrator.

    Defines the contract for all orchestrators in the system.
    The Director uses this interface for cross-feature transitions.

    The class is a singleton — one instance handles requests from all users
    concurrently. No mutable user state in ``self``.
    All context (user_id, chat_id, FSM) is passed through the ``director``.

    Subclasses must implement:
        - ``render_content(payload, director)`` — main rendering logic.

    Subclasses may override:
        - ``handle_entry(director, payload)`` — entry point into the feature.

    Args:
        expected_state: FSM state string set when entering the feature.
                        None — state does not change.

    Example:
        ```python
        class BookingOrchestrator(BaseBotOrchestrator[BookingPayload]):
            def __init__(self):
                super().__init__(expected_state="BookingStates:main")

            async def render_content(
                self, payload: BookingPayload, director: Director
            ) -> ViewResultDTO:
                slots = await self.api.get_slots(director.user_id)
                return ViewResultDTO(text=format_slots(slots), kb=build_kb(slots))
        ```
    """

    def __init__(self, expected_state: str | None = None) -> None:
        self.expected_state = expected_state

    @abstractmethod
    async def render_content(
        self,
        payload: PayloadT,
        director: Director,
    ) -> ViewResultDTO:
        """Main logic for rendering feature content.

        Must be implemented in each specific orchestrator.

        Args:
            payload: Data for rendering (DTO from backend, dict, etc.).
            director: Context of the current request (user_id, chat_id, state).

        Returns:
            ViewResultDTO with text and keyboard.
        """
        ...

    async def handle_entry(
        self,
        director: Director,
        payload: PayloadT | None = None,
    ) -> UnifiedViewDTO:
        """Entry point into the feature. Called by the Director during set_scene().

        The default implementation simply calls render(payload, director).
        Override for complex feature initialization logic.

        Args:
            director: Context of the current request.
            payload: Initial data for rendering.

        Returns:
            UnifiedViewDTO for sending to the user.
        """
        return await self.render(payload, director)

    async def render(
        self,
        payload: PayloadT | None,
        director: Director,
    ) -> UnifiedViewDTO:
        """Assembles UnifiedViewDTO from render_content().

        Enriches the result with data from the director (chat_id, session_key).

        Args:
            payload: Data for rendering.
            director: Context of the current request.

        Returns:
            UnifiedViewDTO ready to be sent via ViewSender.
        """
        content_view = await self.render_content(payload, director)  # type: ignore[arg-type]
        return UnifiedViewDTO(content=content_view, menu=None).model_copy(
            update={
                "chat_id": director.chat_id,
                "session_key": director.user_id,
            }
        )
