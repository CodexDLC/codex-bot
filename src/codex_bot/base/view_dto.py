"""
View DTOs — Immutable response objects from the Orchestrator.

All DTOs are frozen (frozen=True) for safe transfer
between asynchronous services without the risk of race conditions.
If you need to change a field — use model_copy(update={...}).
"""

from typing import Literal

from aiogram.types import InlineKeyboardMarkup
from pydantic import BaseModel, ConfigDict


class ViewResultDTO(BaseModel):
    """DTO for representing a single message (text + keyboard).

    Attributes:
        text: HTML-text of the message.
        kb: Inline keyboard. None — without a keyboard.

    Example:
        ```python
        view = ViewResultDTO(text="Hello!", kb=my_keyboard)
        ```
    """

    text: str
    kb: InlineKeyboardMarkup | None = None

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class MessageCoordsDTO(BaseModel):
    """Telegram message coordinates (chat_id + message_id).

    Attributes:
        chat_id: Chat ID.
        message_id: Message ID in the chat.

    Example:
        ```python
        coords = MessageCoordsDTO(chat_id=123456, message_id=42)
        ```
    """

    chat_id: int
    message_id: int

    model_config = ConfigDict(frozen=True)


class UnifiedViewDTO(BaseModel):
    """Unified immutable response DTO from the Orchestrator.

    Contains optional Menu and Content blocks, as well as metadata
    for routing and UI management (deletion, history clearing).

    Attributes:
        content: Main content block (text + buttons).
        menu: Navigation menu block. None — menu is not updated.
        clean_history: If True — ViewSender will delete previous UI messages.
        alert_text: Text for a popup alert (for CallbackQuery).
        trigger_message_id: ID of the trigger message (e.g., /start) for deletion.
        chat_id: Target chat ID. Filled by the Director.
        session_key: Session key (user_id or channel session). Filled by the Director.
        mode: Sending mode — strictly ``"channel"``, ``"topic"``, or ``"user"``.
        message_thread_id: Topic ID in a supergroup.

    Example:
        ```python
        view = UnifiedViewDTO(
            content=ViewResultDTO(text="Content"),
            menu=ViewResultDTO(text="Menu"),
        )
        # To change chat_id after creation — use model_copy:
        view = view.model_copy(update={"chat_id": 123456})
        ```
    """

    content: ViewResultDTO | None = None
    menu: ViewResultDTO | None = None
    clean_history: bool = False
    alert_text: str | None = None
    trigger_message_id: int | None = None

    # --- Routing & Session (filled by Director) ---
    chat_id: int | str | None = None
    session_key: int | str | None = None
    mode: Literal["channel", "topic", "user"] | None = None
    message_thread_id: int | None = None

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
