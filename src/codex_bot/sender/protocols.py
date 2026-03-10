"""
Protocols for sender — Business interface for UI coordinate storage.

SenderStateStorageProtocol describes operations in terms of the domain area
("UI coordinates") rather than Redis terms (hash, key). The specific implementation
via Redis HASH remains on the project side.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class SenderStateStorageProtocol(Protocol):
    """
    Contract for UI coordinate storage (Menu and Content message IDs).

    Implement this protocol in the project via Redis, PostgreSQL, or in-memory —
    ViewSender and SenderManager do not know about the specific storage.

    Example:
        ```python
        class RedisSenderStorage:
            def __init__(self, redis: Redis): ...

            async def get_sender_state(self, key: str) -> dict[str, int]:
                data = await redis.hgetall(f"sender:{key}")
                return {k: int(v) for k, v in data.items()}

            async def save_sender_state(self, key: str, data: dict[str, int]) -> None:
                await redis.hset(f"sender:{key}", mapping={k: str(v) for k, v in data.items()})

            async def clear_sender_state(self, key: str) -> None:
                await redis.delete(f"sender:{key}")
        ```
    """

    async def get_sender_state(self, key: str) -> dict[str, int]:
        """
        Returns UI coordinates (message IDs) for a session.

        Args:
            key: Session key (e.g., user_id string or channel session_id).

        Returns:
            Dictionary like {"menu_msg_id": 123, "content_msg_id": 124}.
            Empty dictionary if no data exists.
        """
        ...

    async def save_sender_state(self, key: str, data: dict[str, int]) -> None:
        """
        Saves (partially updates) UI coordinates for a session.

        Args:
            key: Session key.
            data: Fields to update, e.g., {"menu_msg_id": 123}.
        """
        ...

    async def clear_sender_state(self, key: str) -> None:
        """
        Deletes all UI coordinates for a session.

        Args:
            key: Session key.
        """
        ...
