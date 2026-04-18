"""
Redis Orchestration - Unified asynchronous event processing layer.

Provides a comprehensive suite of tools for consuming, routing, and
dispatching Redis Stream events. Supports distributed horizontal scaling through
the consumer group pattern and offers per-event dependency injection.
"""

from codex_bot.redis.dispatcher import BotRedisDispatcher, RetrySchedulerProtocol
from codex_bot.redis.router import RedisRouter
from codex_bot.redis.stream_processor import RedisStreamProcessor, StreamStorageProtocol

__all__ = [
    "RedisRouter",
    "BotRedisDispatcher",
    "RetrySchedulerProtocol",
    "RedisStreamProcessor",
    "StreamStorageProtocol",
]
