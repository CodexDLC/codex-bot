"""
ViewSender — STATELESS service for sending and synchronizing Telegram bot UI.

Manages two persistent messages (Menu and Content):
edits them if they exist, creates new ones if not.
Stores their IDs via SenderManager to avoid cluttering the chat.

IMPORTANT: The class must be Stateless — it does not store user state in self.
ViewSender is a singleton. All context is passed through method arguments.
"""

import contextlib
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest

from ..base.view_dto import UnifiedViewDTO, ViewResultDTO
from .sender_manager import SenderManager

log = logging.getLogger(__name__)


class ViewSender:
    """STATELESS service for sending and updating UI messages.

    Works with two persistent bot messages in the chat:

    - **Menu** — navigation block (section buttons).
    - **Content** — information block (current feature data).

    The ``send()`` algorithm:

    1. Deletes the ``trigger_message`` (e.g., the ``/start`` command).
    2. If ``clean_history=True`` — deletes old Menu and Content.
    3. Edits existing messages (or creates new ones).
    4. Saves current ``message_id`` via SenderManager.

    .. note::
        ``alert_text`` from ``UnifiedViewDTO`` is intentionally not processed by ViewSender —
        alert requires access to ``CallbackQuery.answer()``, which ViewSender does not have.
        Call ``await call.answer(view.alert_text)`` in the handler before ``await sender.send(view)``.

    Args:
        bot: Aiogram Bot instance.
        manager: SenderManager for storing UI coordinates.

    Example:
        ```python
        sender = ViewSender(bot=bot, manager=sender_manager)
        # In a handler:
        if view.alert_text:
            await call.answer(view.alert_text, show_alert=True)
        await sender.send(view)
        ```
    """

    def __init__(self, bot: Bot, manager: SenderManager) -> None:
        self.bot = bot
        self.manager = manager

    async def send(self, view: UnifiedViewDTO) -> None:
        """Main UI synchronization method.

        All context variables are local, without writing to self.
        Safe for concurrent calls from different users.

        Args:
            view: ``UnifiedViewDTO`` from the orchestrator. Must contain
                  ``session_key`` and ``chat_id`` (filled by the Director).
        """
        if not view.session_key or not view.chat_id:
            log.error("ViewSender | missing session_key or chat_id in UnifiedViewDTO")
            return

        # Local variables — each send() call is isolated
        key = view.session_key
        chat_id = view.chat_id
        thread_id = view.message_thread_id
        is_channel = self._detect_channel(view)

        # 1. Delete trigger message (e.g., /start)
        if view.trigger_message_id:
            with contextlib.suppress(TelegramAPIError):
                await self.bot.delete_message(
                    chat_id=chat_id,
                    message_id=view.trigger_message_id,
                )

        coords = await self.manager.get_coords(key, is_channel)

        # 2. Clean old UI
        if view.clean_history:
            await self._delete_coords(coords, chat_id)
            coords = {}
            await self.manager.clear_coords(key, is_channel)

        # 3. Update Menu and Content (chat_id and thread_id explicitly via parameters)
        old_menu_id = coords.get("menu_msg_id")
        new_menu_id = await self._process_message(view.menu, old_menu_id, "MENU", chat_id, thread_id)

        old_content_id = coords.get("content_msg_id")
        new_content_id = await self._process_message(view.content, old_content_id, "CONTENT", chat_id, thread_id)

        # 4. Save updated coordinates
        updates: dict[str, int] = {}
        if new_menu_id and new_menu_id != old_menu_id:
            updates["menu_msg_id"] = new_menu_id
        if new_content_id and new_content_id != old_content_id:
            updates["content_msg_id"] = new_content_id

        if updates:
            await self.manager.update_coords(key, updates, is_channel)

    async def _delete_coords(
        self,
        coords: dict[str, int],
        chat_id: int | str,
    ) -> None:
        """Deletes Menu and Content messages from the chat.

        Args:
            coords: Dictionary with ``menu_msg_id`` and ``content_msg_id``.
            chat_id: Chat ID for deletion.
        """
        for msg_id in (coords.get("menu_msg_id"), coords.get("content_msg_id")):
            if msg_id:
                with contextlib.suppress(TelegramAPIError):
                    await self.bot.delete_message(chat_id=chat_id, message_id=msg_id)

    async def _process_message(
        self,
        view_dto: ViewResultDTO | None,
        old_message_id: int | None,
        log_prefix: str,
        chat_id: int | str,
        thread_id: int | None,
    ) -> int | None:
        """Edits an existing message or sends a new one.

        Args:
            view_dto: Content to send. None — skip.
            old_message_id: ID of the existing message to edit.
            log_prefix: Log label (``"MENU"`` or ``"CONTENT"``).
            chat_id: Target chat ID.
            thread_id: Topic ID in a supergroup.

        Returns:
            ID of the current message (old or new). None on error.
        """
        if not view_dto:
            return old_message_id

        if old_message_id:
            try:
                await self.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=old_message_id,
                    text=view_dto.text,
                    reply_markup=view_dto.kb,
                    parse_mode="HTML",
                )
                return old_message_id
            except TelegramBadRequest as e:
                if "message is not modified" in str(e).lower():
                    return old_message_id
                # Message deleted or inaccessible — create new
            except TelegramAPIError:
                pass

        try:
            sent = await self.bot.send_message(
                chat_id=chat_id,
                text=view_dto.text,
                reply_markup=view_dto.kb,
                message_thread_id=thread_id,
                parse_mode="HTML",
            )
            log.debug(f"ViewSender [{log_prefix}] sent | chat={chat_id} msg={sent.message_id}")
            return sent.message_id
        except TelegramAPIError as e:
            log.error(f"ViewSender [{log_prefix}] error | chat={chat_id} error='{e}'")
            return None

    @staticmethod
    def _detect_channel(view: UnifiedViewDTO) -> bool:
        """Detects if the chat is a channel or a group.

        Args:
            view: UnifiedViewDTO with chat data.

        Returns:
            ``True`` if it's a channel, topic, or group with a negative chat_id.
        """
        return (
            view.mode in ("channel", "topic")
            or (isinstance(view.chat_id, int) and view.chat_id < 0)
            or str(view.chat_id).startswith("-")
            or view.message_thread_id is not None
        )
