"""
ContextHelper — Extraction of BaseBotContext from Telegram events.
"""

from aiogram.types import CallbackQuery, Message

from codex_bot.base.context_dto import BaseBotContext


class ContextHelper:
    """
    Helper for extracting BaseBotContext from Message or CallbackQuery.

    Normalizes user_id: if from_user is missing (e.g., a post in a channel),
    it uses chat_id as a fallback for session uniqueness.

    Example:
        ```python
        ctx = ContextHelper.extract_base_context(callback)
        director = Director(container=container, state=state,
                            user_id=ctx.user_id, chat_id=ctx.chat_id)
        ```
    """

    @staticmethod
    def extract_base_context(event: Message | CallbackQuery) -> BaseBotContext:
        """
        Extracts base IDs from an event.

        Args:
            event: Message or CallbackQuery from the user.

        Returns:
            Immutable BaseBotContext with user_id, chat_id, message_id, thread_id.
        """
        user_id = event.from_user.id if event.from_user else 0
        chat_id = user_id
        message_id: int | None = None
        thread_id: int | None = None

        if isinstance(event, CallbackQuery):
            if isinstance(event.message, Message):
                chat_id = event.message.chat.id
                message_id = event.message.message_id
                thread_id = event.message.message_thread_id
            if user_id == 0:
                user_id = chat_id

        elif isinstance(event, Message):
            chat_id = event.chat.id
            message_id = event.message_id
            thread_id = event.message_thread_id
            if user_id == 0:
                user_id = chat_id

        return BaseBotContext(
            user_id=user_id,
            chat_id=chat_id,
            message_id=message_id,
            message_thread_id=thread_id,
        )
