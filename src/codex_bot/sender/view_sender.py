"""
ViewSender — Stateless engine for UI synchronization in Telegram.

The ViewSender manages the lifecycle of persistent UI components (Menu and Content).
It ensures that the bot's interface remains consistent by editing existing
messages or replacing them when necessary, effectively minimizing chat clutter.
"""

from __future__ import annotations

import contextlib
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest

from ..base.view_dto import UnifiedViewDTO, ViewResultDTO
from .sender_manager import SenderManager

log = logging.getLogger(__name__)


class ViewSender:
    """Stateless service for persistent UI orchestration.

    The ViewSender implements a "Dual-Message" UI pattern, maintaining two
    distinct messages per session:

    1. **Menu**: A high-level navigation block for switching features.
    2. **Content**: A dynamic block representing the current feature's state.

    The synchronization algorithm performs atomic updates to these blocks,
    handling message deletion (e.g., of trigger commands) and state
    persistence via an external `SenderManager`.

    Note:
        `alert_text` in `UnifiedViewDTO` is not handled by this service as it
        requires a `CallbackQuery` context. It must be answered manually in
        the handler prior to calling `send()`.

    Args:
        bot: Instance of the `aiogram.Bot` used for Telegram API interactions.
        manager: A `SenderManager` providing access to UI coordinate persistence.
    """

    def __init__(self, bot: Bot, manager: SenderManager) -> None:
        self.bot = bot
        self.manager = manager

    async def send(self, view: UnifiedViewDTO) -> None:
        """Synchronize the current UI state with Telegram.

        Analyzes the `UnifiedViewDTO` to perform required deletions, updates,
        and message deliveries. This method is thread-safe and stateless,
        operating strictly on the provided DTO.

        Args:
            view: The structured UI definition from the orchestrator.
                Must contain valid routing metadata (chat_id, session_key).

        Side Effects:
            - Deletes the trigger message if `trigger_message_id` is present.
            - Updates persistent UI coordinates in the backend storage.
            - Modifies existing messages in the target Telegram chat.
        """
        if not view.session_key or not view.chat_id:
            log.error("ViewSender | missing session_key or chat_id in UnifiedViewDTO")
            return

        # Local variables — each send() call is isolated
        chat_id = view.chat_id
        thread_id = view.message_thread_id
        is_channel = self._detect_channel(view)

        # Logic: In public chats, UI messages are shared.
        # We ignore session_key and bind coordinates to chat/topic ID.
        key = (f"{chat_id}:{thread_id}" if thread_id else str(chat_id)) if is_channel else str(view.session_key)

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
        """Deletes Menu and Content messages from the chat safely.

        Args:
            coords: Dictionary with ``menu_msg_id`` and ``content_msg_id``.
            chat_id: Chat ID for deletion.
        """
        # Use set to avoid double deletion of the same ID and filter None
        msg_ids = set(filter(None, (coords.get("menu_msg_id"), coords.get("content_msg_id"))))

        for msg_id in msg_ids:
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
