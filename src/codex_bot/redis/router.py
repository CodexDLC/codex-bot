"""
RedisRouter — Router for grouping Redis Stream handlers.

Analogous to aiogram.Router, but for messages from Redis Stream.
Allows organizing handlers modularly by feature.
"""

from collections.abc import Callable
from typing import Any

# Types for readability
HandlerFunc = Callable[[dict[str, Any], Any], Any]
FilterFunc = Callable[[dict[str, Any]], bool]


class RedisRouter:
    """
    Router for grouping Redis Stream handlers by message type.

    Used in feature_setting.py of Redis features. After creation,
    it is connected to BotRedisDispatcher via include_router().

    Example:
        ```python
        redis_router = RedisRouter()

        @redis_router.message("notification.created")
        async def handle_notification(payload: dict, container) -> None:
            user_id = payload["user_id"]
            ...

        # With a filter:
        @redis_router.message("notification.created", filter_func=lambda p: p.get("urgent"))
        async def handle_urgent(payload: dict, container) -> None:
            ...
        ```
    """

    def __init__(self) -> None:
        # {message_type: [(handler, filter_func), ...]}
        self._handlers: dict[str, list[tuple[HandlerFunc, FilterFunc | None]]] = {}

    def message(
        self,
        message_type: str,
        filter_func: FilterFunc | None = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """
        Decorator for registering a handler for a Redis Stream message type.

        Args:
            message_type: String message type (e.g., "booking.confirmed").
            filter_func: Optional filter — callable(payload) -> bool.
                         The handler is called only if the filter returns True.

        Returns:
            Decorator returning the original handler unchanged.
        """

        def decorator(handler: HandlerFunc) -> HandlerFunc:
            if message_type not in self._handlers:
                self._handlers[message_type] = []
            self._handlers[message_type].append((handler, filter_func))
            return handler

        return decorator

    @property
    def handlers(self) -> dict[str, list[tuple[HandlerFunc, FilterFunc | None]]]:
        """Registered handlers (read-only view)."""
        return self._handlers
