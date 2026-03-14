"""
Error Orchestration — Redis-backed system error processing.

Orchestrates the lifecycle of 'system_error' events originating from Redis
Streams. Transforms raw event payloads into standardized `UnifiedViewDTO`
objects, facilitating consistent UI error reporting across distributed services.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from codex_bot.base.view_dto import UnifiedViewDTO

from .default_errors import DEFAULT_ERRORS
from .ui import BaseErrorUI, DefaultErrorUI

if TYPE_CHECKING:
    pass


class ErrorOrchestrator:
    """Processes Redis ``system_error`` events and renders error UI.

    Merges ``DEFAULT_ERRORS`` with ``custom_errors`` at construction time
    (custom entries win on key collision). Renders via ``DefaultErrorUI``
    unless a custom ``ui`` is provided.

    Args:
        custom_errors: Additional or override error configs.
                       Dict of ``{error_type: {title, text, button_text, action}}``.
        ui: Custom UI renderer. Must satisfy ``BaseErrorUI`` protocol.
            Defaults to ``DefaultErrorUI``.

    Example:
        ```python
        # Minimal — uses built-in error map and default UI:
        orchestrator = ErrorOrchestrator()

        # With custom errors:
        orchestrator = ErrorOrchestrator(custom_errors=CUSTOM_ERRORS)

        # With custom UI renderer:
        orchestrator = ErrorOrchestrator(ui=MyCustomUI())
        ```
    """

    def __init__(
        self,
        custom_errors: dict[str, dict[str, str]] | None = None,
        ui: BaseErrorUI | None = None,
    ) -> None:
        self._errors_map: dict[str, dict[str, str]] = {
            **DEFAULT_ERRORS,
            **(custom_errors or {}),
        }
        self._ui: BaseErrorUI = ui or DefaultErrorUI()

    def handle_error(self, message_data: dict[str, object]) -> UnifiedViewDTO:
        """Build a ``UnifiedViewDTO`` from a Redis ``system_error`` event.

        Looks up ``error_type`` in the errors map, renders the UI,
        and wraps the result with ``user_id`` / ``chat_id`` from the event.

        Falls back to the ``"default"`` error config if ``error_type`` is
        unknown or missing.

        Args:
            message_data: Dict from Redis Stream. Expected keys:
                ``error_type`` (str), ``user_id`` (str|int), ``chat_id`` (str|int).

        Returns:
            ``UnifiedViewDTO`` with ``content``, ``session_key``, and ``chat_id`` filled.
        """
        error_type = str(message_data.get("error_type", "default"))
        config = self._errors_map.get(error_type, self._errors_map["default"])
        content = self._ui.render_error(config)

        raw_user_id = message_data.get("user_id")
        raw_chat_id = message_data.get("chat_id")

        session_key = int(str(raw_user_id)) if raw_user_id is not None else None
        chat_id = int(str(raw_chat_id)) if raw_chat_id is not None else None

        return UnifiedViewDTO(content=content).model_copy(update={"session_key": session_key, "chat_id": chat_id})
