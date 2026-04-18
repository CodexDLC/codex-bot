"""
Identity Inspection - Developer-centric diagnostic utility.

Provides specialized handlers for analyzing Telegram-native update metadata,
specifically optimized for identifying polymorphic entity IDs (Users, Chats,
Channels, Threads) during the development and orchestration phases.
"""

from typing import Any

from aiogram.types import CallbackQuery, Message, TelegramObject

from codex_bot.base.context_dto import BaseBotContext


class ContextHelper:
    """Utility class for polymorphic context extraction.

    Standardizes the retrieval of identity and routing information across
    different interaction models. It ensures that business logic receives
    a consistent `BaseBotContext` regardless of the upstream event source.

    Capabilities:
        - Parsing `aiogram.Message` and `aiogram.CallbackQuery`.
        - Normalizing raw dictionaries (Redis Stream / Direct API).
        - Handling fallback logic for user/chat identity resolution.
    """

    @staticmethod
    def extract_base_context(event: TelegramObject | dict[str, Any]) -> BaseBotContext:
        """Analyze an event source and extract its routing metadata.

        Coordinates the extraction of User ID, Chat ID, and Thread IDs,
        applying normalization rules to ensure session consistency.

        Args:
            event: A native Telegram object or a dictionary representing
                an incoming event payload.

        Returns:
            An immutable `BaseBotContext` populated with the extracted IDs.
        """
        user_id: int = 0
        chat_id: int = 0
        message_id: int | None = None
        thread_id: int | None = None

        # 1. Handling aiogram objects
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else 0
            chat_id = event.chat.id
            message_id = event.message_id
            thread_id = event.message_thread_id

        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            if event.message and isinstance(event.message, Message):
                chat_id = event.message.chat.id
                message_id = event.message.message_id
                thread_id = event.message.message_thread_id
            else:
                chat_id = user_id

        # 2. Handling raw dictionaries (Redis / API)
        elif isinstance(event, dict):
            user_id = event.get("user_id") or event.get("from_id") or 0
            chat_id = event.get("chat_id") or user_id
            message_id = event.get("message_id") or event.get("trigger_id")
            thread_id = event.get("thread_id") or event.get("message_thread_id")

        # 3. Final normalization
        # Fallback: if user_id is missing but we have chat_id, use chat_id as session key
        if user_id == 0 and chat_id != 0:
            user_id = chat_id

        # If we still have no IDs, return default zeros (to avoid None errors in Director)
        return BaseBotContext(
            user_id=int(user_id),
            chat_id=int(chat_id),
            message_id=int(message_id) if message_id else None,
            message_thread_id=int(thread_id) if thread_id else None,
        )
