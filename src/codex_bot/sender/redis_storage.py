"""
RedisSenderStorage — High-performance Redis HASH implementation for UI coordinates.

Uses native Redis Hashes to store and update message IDs, providing
atomic operations and efficient memory usage.
"""

from __future__ import annotations

from typing import Any

from .protocols import SenderStateStorageProtocol


class RedisSenderStorage(SenderStateStorageProtocol):
    """Redis storage implementation using HASHES.

    Coordinates are stored as fields within a Redis Hash, allowing
    partial updates (e.g. only updating menu_msg_id) without rewriting
    the entire record.

    Args:
        redis: An initialized Redis client (redis.asyncio).
        ttl: Time-to-live for coordinate keys in seconds (default: 7 days).
    """

    def __init__(self, redis: Any, ttl: int = 604800) -> None:
        self.redis = redis
        self.ttl = ttl

    async def get_sender_state(self, key: str) -> dict[str, int]:
        """Retrieves coordinates using HGETALL.

        Args:
            key: Prepared Redis key from SenderManager.

        Returns:
            Dictionary with coordinates. Keys and values are cast to correct types.
        """
        data = await self.redis.hgetall(key)
        if not data:
            return {}

        # Redis returns strings/bytes, we cast them back to integers
        return {k: int(v) for k, v in data.items()}

    async def save_sender_state(self, key: str, data: dict[str, int]) -> None:
        """Saves or updates coordinates using HSET.

        Args:
            key: Prepared Redis key.
            data: Fields to update (e.g. {"menu_msg_id": 123}).
        """
        if not data:
            return

        # Atomic update of multiple fields in the hash
        await self.redis.hset(name=key, mapping=data)

        # Refresh TTL on every update
        await self.redis.expire(name=key, time=self.ttl)

    async def clear_sender_state(self, key: str) -> None:
        """Removes the entire hash key from Redis.

        Args:
            key: Prepared Redis key.
        """
        await self.redis.delete(key)
