"""
Identity Inspection - Developer-centric diagnostic utility.

Provides specialized handlers for analyzing Telegram-native update metadata,
specifically optimized for identifying polymorphic entity IDs (Users, Chats,
Channels, Threads) during the development and orchestration phases.
"""

from aiogram.types import Message


async def inspect_ids_handler(message: Message) -> None:
    """
    Ready-to-use aiogram handler for inspecting IDs.

    Returns User ID, Chat ID, Chat Type, and Thread ID.
    Supports forwarded messages from channels to find Channel IDs.

    Usage:
        ```python
        from codex_bot.helper.id_inspector import inspect_ids_handler
        router.message(Command("id"))(inspect_ids_handler)
        ```
    """
    chat_type = message.chat.type
    user_id = message.from_user.id if message.from_user else "Unknown"

    report = (
        "🆔 <b>ID Inspector</b>\n"
        "──────────────────\n"
        f"👤 <b>User ID:</b> <code>{user_id}</code>\n"
        f"💬 <b>Chat ID:</b> <code>{message.chat.id}</code>\n"
        f"🏗 <b>Chat Type:</b> <code>{chat_type}</code>\n"
    )

    if message.message_thread_id:
        report += f"🧵 <b>Thread ID:</b> <code>{message.message_thread_id}</code>\n"

    if message.reply_to_message and message.reply_to_message.forward_from_chat:
        f_chat = message.reply_to_message.forward_from_chat
        report += f"📢 <b>Forwarded Chat ID:</b> <code>{f_chat.id}</code>\n"

    await message.reply(report, parse_mode="HTML")
