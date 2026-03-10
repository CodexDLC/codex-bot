"""
RedisStreamProcessor — Redis Stream polling loop (Consumer Group).

Reads messages from Redis Stream via a Consumer Group, passes them
to a callback function (usually BotRedisDispatcher.process_message),
and acknowledges successful processing via ACK.
"""

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, runtime_checkable

log = logging.getLogger(__name__)


@runtime_checkable
class StreamStorageProtocol(Protocol):
    """
    Redis Stream adapter protocol for RedisStreamProcessor.

    Implement in the project on top of redis-py or any other client.

    Example:
        ```python
        class RedisStreamAdapter:
            def __init__(self, redis: Redis): self.redis = redis

            async def create_group(self, stream: str, group: str) -> None:
                with contextlib.suppress(ResponseError):
                    await self.redis.xgroup_create(stream, group, id="0", mkstream=True)

            async def read_events(self, stream_name, group_name, consumer_name, count):
                result = await self.redis.xreadgroup(
                    group_name, consumer_name, {stream_name: ">"}, count=count, block=0
                )
                if not result:
                    return []
                return [(msg_id, data) for _, messages in result for msg_id, data in messages]

            async def ack_event(self, stream_name, group_name, message_id) -> None:
                await self.redis.xack(stream_name, group_name, message_id)
        ```
    """

    async def create_group(self, stream_name: str, group_name: str) -> None:
        """Creates a Consumer Group (idempotently)."""
        ...

    async def read_events(
        self,
        stream_name: str,
        group_name: str,
        consumer_name: str,
        count: int,
    ) -> list[tuple[str, dict[str, Any]]]:
        """
        Reads a batch of unread messages from the group.

        Returns:
            List of pairs (message_id, data_dict).
        """
        ...

    async def ack_event(self, stream_name: str, group_name: str, message_id: str) -> None:
        """Acknowledges message processing (XACK)."""
        ...


MessageCallback = Callable[[dict[str, Any]], Awaitable[None]]


class RedisStreamProcessor:
    """
    Redis Stream processor: reads messages and passes them to a callback.

    Starts a background asyncio task (_consume_loop) that continuously
    reads messages from Redis Stream via a Consumer Group.
    On errors — recreates the group (e.g., after a Redis restart).

    Args:
        storage: Stream adapter (StreamStorageProtocol).
        stream_name: Redis Stream name (e.g., "bot_events").
        consumer_group_name: Consumer Group name.
        consumer_name: Unique consumer name (e.g., "bot-worker-1").
        batch_count: Number of messages per reading cycle.
        poll_interval: Wait interval (sec) if there are no messages.

    Example:
        ```python
        processor = RedisStreamProcessor(
            storage=redis_stream_adapter,
            stream_name="bot_events",
            consumer_group_name="bot_group",
            consumer_name="bot-1",
        )
        processor.set_message_callback(dispatcher.process_message)
        await processor.start_listening()
        ```
    """

    def __init__(
        self,
        storage: StreamStorageProtocol,
        stream_name: str,
        consumer_group_name: str,
        consumer_name: str,
        batch_count: int = 10,
        poll_interval: float = 1.0,
    ) -> None:
        self.storage = storage
        self.stream_name = stream_name
        self.group_name = consumer_group_name
        self.consumer_name = consumer_name
        self.batch_count = batch_count
        self.poll_interval = poll_interval

        self.is_running = False
        self._callback: MessageCallback | None = None
        self._task: asyncio.Task[None] | None = None

    def set_message_callback(self, callback: MessageCallback) -> None:
        """
        Sets the callback for processing each message.

        Args:
            callback: Async callable(payload: dict) -> None.
        """
        self._callback = callback

    async def start_listening(self) -> None:
        """
        Starts the background Stream reading loop.

        Creates a Consumer Group (up to 5 attempts), then starts _consume_loop
        as an asyncio Task.
        """
        if self.is_running:
            log.warning("RedisStreamProcessor | already running")
            return

        for attempt in range(1, 6):
            try:
                await self.storage.create_group(self.stream_name, self.group_name)
                break
            except Exception as e:
                log.warning(f"RedisStreamProcessor | create_group attempt {attempt}/5: {e}")
                if attempt < 5:
                    await asyncio.sleep(3)
                else:
                    log.error("RedisStreamProcessor | failed to create group, giving up")
                    return

        self.is_running = True
        self._task = asyncio.create_task(self._consume_loop())
        log.info(
            f"RedisStreamProcessor | listening stream='{self.stream_name}' "
            f"group='{self.group_name}' consumer='{self.consumer_name}'"
        )

    async def stop_listening(self) -> None:
        """Stops the reading loop and correctly cancels the asyncio Task."""
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        log.info("RedisStreamProcessor | stopped")

    async def _consume_loop(self) -> None:
        try:
            while self.is_running:
                try:
                    messages = await self.storage.read_events(
                        stream_name=self.stream_name,
                        group_name=self.group_name,
                        consumer_name=self.consumer_name,
                        count=self.batch_count,
                    )

                    if not messages:
                        await asyncio.sleep(self.poll_interval)
                        continue

                    for message_id, data in messages:
                        await self._process_single(message_id, data)

                except asyncio.CancelledError:
                    raise  # propagate immediately, do not catch in general except
                except Exception as e:
                    log.error(f"RedisStreamProcessor | consume loop error: {e}")
                    if "NOGROUP" in str(e):
                        log.warning("RedisStreamProcessor | consumer group missing, recreating...")
                        try:
                            await self.storage.create_group(self.stream_name, self.group_name)
                        except Exception as create_err:
                            log.error(f"RedisStreamProcessor | recreate failed: {create_err}")
                    await asyncio.sleep(5)
        except asyncio.CancelledError:
            log.info("RedisStreamProcessor | consume loop cancelled")
            raise  # asyncio requires propagating CancelledError

    async def _process_single(self, message_id: str, data: dict[str, Any]) -> None:
        try:
            if self._callback:
                await self._callback(data)
            await self.storage.ack_event(self.stream_name, self.group_name, message_id)
        except Exception as e:
            log.error(f"RedisStreamProcessor | failed to process message {message_id}: {e}")
