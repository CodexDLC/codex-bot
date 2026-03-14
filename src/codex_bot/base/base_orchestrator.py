"""
BaseBotOrchestrator — Abstract base for stateless feature orchestrators.

Orchestrators serve as the core logic controllers for specific features. They
transform business payloads into visual DTOs. Following the Stateless Singleton
pattern, a single instance handles concurrent requests by receiving all
necessary context via method arguments.
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
    """Abstract base class for feature-specific orchestrators.

    Implements the `OrchestratorProtocol` and provides a template for
    rendering UI responses. Orchestrators are designed as stateless services
    that operate on a request-scoped `Director` context.

    Note:
        Subclasses must be thread-safe for use in `asyncio` loops as they are
        typically registered as singletons in the DI container.

    Args:
        expected_state: The FSM state string to be set by the `Director`
            when this feature is entered. If None, the state remains unchanged.

    Example:
        ```python
        class ProfileOrchestrator(BaseBotOrchestrator[ProfilePayload]):
            async def render_content(self, director, payload):
                return ViewResultDTO(text=f"User: {payload.name}")
        ```
    """

    def __init__(self, expected_state: str | None = None) -> None:
        self.expected_state = expected_state

    @abstractmethod
    async def render_content(
        self,
        director: Director | None = None,
        payload: PayloadT | None = None,
    ) -> ViewResultDTO | UnifiedViewDTO:
        """Analyze business data and generate the primary UI components.

        This is the primary extension point for feature logic. It must process
         the payload and return the visual representation of the feature.

        Args:
            director: Request-scoped coordinator providing access to DI and session.
            payload: Domain-specific data required for rendering.

        Returns:
            A `ViewResultDTO` for standard responses or `UnifiedViewDTO` for
            complex responses or redirects.
        """
        ...

    async def handle_entry(
        self,
        director: Director,
        payload: PayloadT | None = None,
    ) -> UnifiedViewDTO:
        """Entry point into the feature. Called by the Director during set_scene().

        The default implementation simply calls render(director, payload).
        Override for complex feature initialization logic.

        Args:
            director: Context of the request.
            payload: Initial data for rendering.

        Returns:
            UnifiedViewDTO for sending to the user.
        """
        return await self.render(director=director, payload=payload)

    async def render(
        self,
        director: Director | None = None,
        payload: PayloadT | None = None,
    ) -> UnifiedViewDTO:
        """Assemble a `UnifiedViewDTO` by executing the rendering logic.

        Wraps the result of `render_content` into a standardized delivery
        format. Handles automatic enrichment for standard response types.

        Args:
            director: Current request context.
            payload: Data to be rendered.

        Returns:
            A fully structured `UnifiedViewDTO` ready for transmission.
        """
        # Internal library calls now strictly use keyword arguments for safety
        view = await self.render_content(director=director, payload=payload)

        # If render_content already returned a full UnifiedViewDTO (Redirect)
        res = view if isinstance(view, UnifiedViewDTO) else UnifiedViewDTO(content=view, menu=None)

        # Session enrichment (chat_id, session_key) from the Director context
        if director:
            res = res.model_copy(
                update={
                    "chat_id": res.chat_id or director.chat_id,
                    "session_key": res.session_key or director.user_id,
                    "trigger_message_id": res.trigger_message_id or director.trigger_id,
                }
            )

        return res
