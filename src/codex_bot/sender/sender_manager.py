"""
SenderManager — Manager of UI coordinates (message IDs in Telegram).

Stores message_ids of two persistent bot messages (Menu and Content),
so that ViewSender can edit them instead of sending new ones.
"""

from codex_bot.sender.protocols import SenderStateStorageProtocol
from codex_bot.sender.sender_keys import SenderKeys


class SenderManager:
    """
    Manager for UI coordinate storage.

    Abstracts work with coordinates (menu_msg_id, content_msg_id)
    on top of SenderStateStorageProtocol. ViewSender works only through it.

    Args:
        storage: Implementation of SenderStateStorageProtocol (Redis, in-memory, etc.).

    Example:
        ```python
        manager = SenderManager(storage=redis_sender_storage)
        coords = await manager.get_coords(session_key=123456)
        # {"menu_msg_id": 10, "content_msg_id": 11}

        await manager.update_coords(123456, {"menu_msg_id": 20})
        await manager.clear_coords(123456)
        ```
    """

    def __init__(self, storage: SenderStateStorageProtocol) -> None:
        self.storage = storage

    async def get_coords(self, session_key: int | str, is_channel: bool = False) -> dict[str, int]:
        """
        Returns saved UI coordinates for a session.

        Args:
            session_key: user_id (int) or session_id (str) for a channel.
            is_channel: True — use channel key, False — use user key.

        Returns:
            Dictionary {"menu_msg_id": int, "content_msg_id": int}.
            Empty dictionary if no data exists.
        """
        key = self._build_key(session_key, is_channel)
        return await self.storage.get_sender_state(key)

    async def update_coords(
        self,
        session_key: int | str,
        coords: dict[str, int],
        is_channel: bool = False,
    ) -> None:
        """
        Partially updates UI coordinates for a session.

        Args:
            session_key: user_id or session_id.
            coords: Fields to update (partial update).
            is_channel: Key type.
        """
        if not coords:
            return
        key = self._build_key(session_key, is_channel)
        await self.storage.save_sender_state(key, coords)

    async def clear_coords(self, session_key: int | str, is_channel: bool = False) -> None:
        """
        Deletes all UI coordinates for a session (state reset).

        Args:
            session_key: user_id or session_id.
            is_channel: Key type.
        """
        key = self._build_key(session_key, is_channel)
        await self.storage.clear_sender_state(key)

    @staticmethod
    def _build_key(session_key: int | str, is_channel: bool) -> str:
        if is_channel:
            return SenderKeys.channel(str(session_key))
        return SenderKeys.user(session_key)
