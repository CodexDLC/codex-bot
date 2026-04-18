"""
View DTOs — Immutable response objects for the presentation layer.

This module defines Data Transfer Objects (DTOs) used by orchestrators to
encapsulate UI state. All DTOs are immutable (frozen) to ensure thread-safety
and prevent unintended side effects during transfer between asynchronous services.
"""

from typing import Any, Literal

from aiogram.types import InlineKeyboardMarkup
from pydantic import BaseModel, ConfigDict


class ViewResultDTO(BaseModel):
    """Data Transfer Object representing a single Telegram message.

    Encapsulates the visual components of a message, including its textual
    content and interactive elements. Designed for use within `UnifiedViewDTO`.

    Attributes:
        text: HTML-formatted string containing the message body.
        kb: Optional inline keyboard markup for user interaction.

    Example:
        ```python
        view = ViewResultDTO(text="<b>Success!</b>", kb=inline_kb)
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
    """Unified response DTO for cross-service UI synchronization.

    This DTO serves as the primary contract between orchestrators and the
    `ViewSender`. It aggregates multiple UI components (menus, content)
    and routing metadata required for complex interaction flows.

    Attributes:
        content: Primary content block representing the main response message.
        menu: Optional navigation menu block for persistent UI elements.
        clean_history: If True, instructs the sender to prune previous UI messages.
        alert_text: Plain text for CallbackQuery toast notifications.
        trigger_message_id: ID of the message that initiated the request (for cleanup).
        chat_id: Target destination for the UI update. Populated by the `Director`.
        session_key: Identifier for user or channel session isolation.
        mode: Telegram delivery mode (channel/topic/user).
        message_thread_id: Destination thread ID for supergroup topics.

    Example:
        ```python
        view = UnifiedViewDTO(
            content=ViewResultDTO(text="Operation completed."),
            clean_history=True
        )
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

    async def send(self, message: Any, i18n: Any = None) -> Any:
        """
        Backward compatibility bridge for generated handlers.
        Sends the content part of the DTO to the user.
        """
        if not self.content:
            return None

        return await message.answer(text=self.content.text, reply_markup=self.content.kb, parse_mode="HTML")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)
