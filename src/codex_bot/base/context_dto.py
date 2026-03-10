"""
Context DTOs — Immutable context of a Telegram event.

BaseBotContext contains the minimum necessary set of data
for any orchestrator to work: user_id, chat_id, message_id.
"""

from pydantic import BaseModel, ConfigDict


class BaseBotContext(BaseModel):
    """
    Base immutable context for a Telegram event.

    Extracted from Message or CallbackQuery via ContextHelper.
    Contains only identifiers — no business logic.

    Attributes:
        user_id: Telegram ID of the user. Used as a session key.
        chat_id: ID of the chat (private, group, channel).
        message_id: ID of the message that triggered the event.
        message_thread_id: ID of the topic in a supergroup (if applicable).
        session_key: Key for state storage (defaults to user_id).

    Example:
        ```python
        ctx = BaseBotContext(user_id=123, chat_id=123, message_id=42)
        print(ctx.session_key)  # 123
        ```
    """

    user_id: int
    chat_id: int
    message_id: int | None = None
    message_thread_id: int | None = None

    model_config = ConfigDict(frozen=True)

    @property
    def session_key(self) -> int:
        """Key for storing state in Redis (defaults to user_id)."""
        return self.user_id
