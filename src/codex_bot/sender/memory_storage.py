"""
MemorySenderStorage — In-memory implementation of UI coordinate storage.

Allows the ViewSender to function without a Redis backend by storing message IDs
directly in the bot's RAM. All data is lost when the process restarts.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .protocols import SenderStateStorageProtocol

if TYPE_CHECKING:
    pass


class MemorySenderStorage(SenderStateStorageProtocol):
    """In-memory storage for UI coordinates.

    Ideal for lightweight bots or development environments where Redis is not available.
    Data is stored in a local dictionary and persists only for the duration
    of the bot's process life.

    Example:
        ```python
        if not settings.use_redis:
            storage = MemorySenderStorage()
            manager = SenderManager(storage=storage)
            view_sender = ViewSender(bot=bot, manager=manager)
        ```
    """

    def __init__(self) -> None:
        """Initializes the local storage dictionary."""
        self._storage: dict[str, dict[str, int]] = {}

    async def get_sender_state(self, key: str) -> dict[str, int]:
        """Retrieves coordinates from memory.

        Args:
            key: Storage key (e.g., "sender:user:123").

        Returns:
            A copy of the coordinate dictionary. Returns an empty dict if not found.
        """
        data = self._storage.get(key, {})
        # Return a copy to prevent accidental mutations by reference
        return data.copy()

    async def save_sender_state(self, key: str, data: dict[str, int]) -> None:
        """Saves or updates coordinates in memory.

        Args:
            key: Storage key.
            data: Dictionary with updated coordinates (e.g., {"menu_msg_id": 42}).
        """
        if key not in self._storage:
            self._storage[key] = {}

        self._storage[key].update(data)

    async def clear_sender_state(self, key: str) -> None:
        """Removes coordinates for the specified key from memory.

        Args:
            key: Storage key to clear.
        """
        self._storage.pop(key, None)
