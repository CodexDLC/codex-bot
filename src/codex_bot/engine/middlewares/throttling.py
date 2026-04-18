"""
Atomic Rate Limiting — Redis-backed update orchestration.

Implements high-performance throttling using the atomic `SET NX` operation.
Designed to eliminate race conditions in concurrent update flows and
minimize Redis round-trips by combining validation and persistence logic.
"""

import logging
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

log = logging.getLogger(__name__)


class ThrottlingMiddleware(BaseMiddleware):
    """
    Rate limiting middleware via atomic Redis SET NX.

    One network request instead of two (EXISTS + SET).
    Atomicity eliminates race conditions during parallel updates.

    Args:
        redis: Async Redis client (``redis.asyncio.Redis``).
        rate_limit: Minimum interval between requests in seconds.
                    Supports fractional values (e.g., ``0.5``).

    Example:
        ```python
        from redis.asyncio import Redis
        from codex_bot.engine.middlewares import ThrottlingMiddleware

        redis = Redis.from_url("redis://localhost")
        builder.add_middleware(ThrottlingMiddleware(redis=redis, rate_limit=0.5))
        ```
    """

    def __init__(self, redis: Any, rate_limit: float = 1.0) -> None:
        self.redis = redis
        self.rate_limit = rate_limit

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user_id: int | None = event.from_user.id if hasattr(event, "from_user") and event.from_user else None

        if not user_id:
            return await handler(event, data)

        key = f"throttle:{user_id}"

        # Atomic operation: creates a key with TTL only if it didn't exist.
        # Returns True on creation, None if the key already existed.
        # px = milliseconds, supports fractional rate_limit (0.5 → 500 ms)
        is_new = await self.redis.set(key, "1", px=int(self.rate_limit * 1000), nx=True)

        if not is_new:
            log.warning(f"Throttling | user={user_id} blocked")
            if isinstance(event, CallbackQuery):
                await event.answer("⏳ Not so fast!", show_alert=False)
            return None

        return await handler(event, data)
