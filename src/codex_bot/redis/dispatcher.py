"""
Redis Orchestration — Unified asynchronous event processing layer.

Provides a comprehensive suite of tools for consuming, routing, and
dispatching Redis Stream events. Supports distributed horizontal scaling through
the consumer group pattern and offers per-event dependency injection.
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .router import FilterFunc, HandlerFunc, RedisRouter

log = logging.getLogger(__name__)


@runtime_checkable
class RetrySchedulerProtocol(Protocol):
    """Protocol for a retry scheduler (ARQ or similar).

    Implement and pass to BotRedisDispatcher for automatic
    rescheduling of failed messages to a retry queue.
    """

    async def schedule_retry(self, stream_name: str, payload: dict[str, Any], delay: int = 60) -> None:
        """Schedules message reprocessing.

        Args:
            stream_name: Redis Stream name.
            payload: Message data for reprocessing.
            delay: Delay in seconds before retry.
        """
        ...


class BotRedisDispatcher:
    """Redis Stream message dispatcher for a Telegram bot.

    Allows registering handlers via decorators or routers. Orchestrates the
    dispatching of incoming messages by type, supporting filtering and
    automated retry scheduling via external protocols.

    Args:
        retry_scheduler: Optional retry scheduler (ARQ, etc.).

    Example:
        ```python
        dispatcher = BotRedisDispatcher()

        @dispatcher.on_message("booking.confirmed")
        async def on_booking(payload: dict, container) -> None:
            await container.notification_service.send(payload["user_id"])

        # Connecting a router from a feature:
        dispatcher.include_router(notifications_redis_router)

        # Setting dependencies before start:
        dispatcher.setup(container=container)
        await dispatcher.process_message({"type": "booking.confirmed", ...})
        ```
    """

    def __init__(self, retry_scheduler: RetrySchedulerProtocol | None = None) -> None:
        """Initializes the dispatcher with an empty router list.

        Args:
            retry_scheduler: Optional service for message retries.
        """
        self._container: Any | None = None
        self._retry_scheduler = retry_scheduler
        self._handlers: dict[str, list[tuple[HandlerFunc, FilterFunc | None]]] = {}
        log.info("BotRedisDispatcher | initialized")

    def setup(self, container: Any) -> None:
        """Sets the DI container before processing begins.

        If a handler needs a Bot to send messages - it retrieves it
        directly from ``container.bot``.

        Args:
            container: Project's DI container.
        """
        self._container = container

    def include_router(self, router: RedisRouter) -> None:
        """Connects a RedisRouter with its handlers.

        Args:
            router: Router from a feature.
        """
        for message_type, handlers in router.handlers.items():
            if message_type not in self._handlers:
                self._handlers[message_type] = []
            self._handlers[message_type].extend(handlers)
        log.info(f"BotRedisDispatcher | included router types={list(router.handlers.keys())}")

    def on_message(
        self,
        message_type: str,
        filter_func: FilterFunc | None = None,
    ) -> Callable[[HandlerFunc], HandlerFunc]:
        """Decorator for registering a handler directly in the dispatcher.

        Args:
            message_type: Redis Stream message type.
            filter_func: Optional payload -> bool filter.

        Returns:
            Decorator function.
        """

        def decorator(handler: HandlerFunc) -> HandlerFunc:
            if message_type not in self._handlers:
                self._handlers[message_type] = []
            self._handlers[message_type].append((handler, filter_func))
            return handler

        return decorator

    async def process_message(self, message_data: dict[str, Any], stream_name: str = "bot_events") -> None:
        """Dispatches an incoming Redis Stream message.

        Args:
            message_data: Message payload. Required field: ``"type"``.
            stream_name: Redis Stream name for retry scheduling. Defaults to ``"bot_events"``.
        """
        if not self._container:
            log.error("BotRedisDispatcher | container not set — call setup() first")
            return

        msg_type = message_data.get("type")
        if not msg_type:
            log.warning(f"BotRedisDispatcher | message without 'type' field: {message_data}")
            return

        handlers = self._handlers.get(msg_type, [])
        if not handlers:
            log.debug(f"BotRedisDispatcher | no handlers for type='{msg_type}'")
            return

        for handler, filter_func in handlers:
            try:
                # Filter check
                if filter_func is None or filter_func(message_data):
                    log.debug(f"BotRedisDispatcher | calling {handler.__name__} for type='{msg_type}'")
                    await handler(message_data, self._container)
            except Exception as e:
                log.error(f"BotRedisDispatcher | handler {handler.__name__} failed: {e}")

                # Attempt to schedule retry if scheduler is available
                if self._retry_scheduler:
                    try:
                        await self._retry_scheduler.schedule_retry(
                            stream_name=stream_name,
                            payload=message_data,
                            delay=60,
                        )
                        log.info(f"BotRedisDispatcher | retry scheduled for type='{msg_type}'")
                        # Responsibility passed to scheduler — ACK will occur in processor
                        return
                    except Exception as retry_err:
                        log.error(f"BotRedisDispatcher | retry scheduling failed: {retry_err}")

                # No scheduler or it failed — re-raise, no ACK (PEL)
                raise
