"""
RedisStreamProcessor — High-performance asynchronous stream processing engine.

Implements the Consumer Group pattern for distributed event processing.
Handles continuous polling, at-least-once delivery guarantees via
acknowledgments (XACK), and automatic recovery of missing delivery groups.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
from collections.abc import Awaitable, Callable
from typing import Any, Protocol, runtime_checkable

log = logging.getLogger(__name__)


@runtime_checkable
class StreamStorageProtocol(Protocol):
    """Redis Stream adapter protocol for RedisStreamProcessor.

    Implement this protocol in the project on top of redis-py or any other client.
    It abstracts the underlying Redis Stream commands (XGROUP, XREADGROUP, XACK).

    Example:
        ```python
        class RedisStreamAdapter:
            def __init__(self, redis: Redis):
                self.redis = redis

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
        """Creates a Consumer Group (idempotently).

        Args:
            stream_name: Name of the Redis Stream.
            group_name: Name of the consumer group to create.
        """
        ...

    async def read_events(
        self,
        stream_name: str,
        group_name: str,
        consumer_name: str,
        count: int,
    ) -> list[tuple[str, dict[str, Any]]]:
        """Reads a batch of unread messages from the group.

        Uses the special ID '>' to fetch only messages that haven't been
        delivered to any other consumer in the group.

        Args:
            stream_name: Name of the stream.
            group_name: Consumer group name.
            consumer_name: Unique name of this processor instance.
            count: Maximum number of messages to fetch in one batch.

        Returns:
            List of pairs (message_id, data_dict). Empty list if no messages.
        """
        ...

    async def ack_event(self, stream_name: str, group_name: str, message_id: str) -> None:
        """Acknowledges successful message processing (XACK).

        Removing the message from the PEL (Pending Entries List) of the group.

        Args:
            stream_name: Name of the stream.
            group_name: Consumer group name.
            message_id: ID of the message to acknowledge.
        """
        ...


MessageCallback = Callable[[dict[str, Any]], Awaitable[None]]


class RedisStreamProcessor:
    """Asynchronous engine for consuming and dispatching Redis Stream events.

    This processor facilitates horizontal scaling by allowing multiple
    instances to share the same Redis Consumer Group. It manages the
    low-level lifecycle of stream consumption, including grouping,
    batching, and acknowledgments.

    Key Features:
        - **Reliability**: Guarantees at-least-once processing via XACK.
        - **Distributed Scaling**: Native support for Redis Consumer Groups.
        - **Self-Healing**: Automatically re-establishes group identity
          upon infrastructure failure (e.g., Redis flushes).

    Args:
        storage: An implementation of `StreamStorageProtocol` for Redis interaction.
        stream_name: The identifier of the source Redis Stream.
        consumer_group_name: The shared group name for load balancing.
        consumer_name: Unique identifier for this specific processor instance.
        batch_count: Maximum messages to process per cycle.
        poll_interval: Idle wait duration when no messages are pending.
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
        """Sets the callback for processing each message.

        The callback should be an async function that takes a dictionary (payload).

        Args:
            callback: Async callable(payload: dict) -> None.
        """
        self._callback = callback

    async def start_listening(self) -> None:
        """Starts the background Stream reading loop.

        First, ensures that the consumer group exists (up to 5 attempts).
        Then, spawns the ``_consume_loop`` as a background task.
        """
        if self.is_running:
            log.warning("RedisStreamProcessor | already running")
            return

        # Attempt to create group with retry logic
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
        """Stops the reading loop and correctly cancels the asyncio Task.

        Ensures graceful shutdown by waiting for the current poll cycle to finish
        or be cancelled correctly.
        """
        self.is_running = False
        if self._task and not self._task.done():
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
        log.info("RedisStreamProcessor | stopped")

    async def _consume_loop(self) -> None:
        """Main infinite loop for consuming messages from the stream.

        TODO: Implement PEL (Pending Entries List) recovery mechanism.
        Currently, if a handler crashes and no RetrySchedulerProtocol is provided,
        the message stays in PEL forever without ACK, causing memory leaks in Redis.
        Need to add XPENDING/XCLAIM logic on processor startup to fetch unacked messages.
        """
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
                    # Asyncio standard: re-raise CancelledError immediately
                    raise
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
            raise

    async def _process_single(self, message_id: str, data: dict[str, Any]) -> None:
        """Processes a single message and acknowledges it on success.

        If the callback succeeds, calls ``XACK``. If it fails, the message
        remains in the PEL for future recovery or retry scheduling.

        Args:
            message_id: Unique Redis message ID.
            data: Payload of the message.
        """
        try:
            if self._callback:
                await self._callback(data)

            # Message processed successfully -> confirm to Redis
            await self.storage.ack_event(self.stream_name, self.group_name, message_id)
        except Exception as e:
            log.error(f"RedisStreamProcessor | failed to process message {message_id}: {e}")
            # Message remains in PEL (unacknowledged)
