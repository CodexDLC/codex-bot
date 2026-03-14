# redis — Redis Stream processing and event routing

Infrastructure for building Event-Driven architecture based on Redis Streams.

## Dispatcher
Central hub for event distribution.

::: codex_bot.redis.dispatcher.BotRedisDispatcher

---

## Stream Processor
Polling loop for event streams (Consumer Group).

::: codex_bot.redis.stream_processor.RedisStreamProcessor

---

## Router
Tool for registering event handlers.

::: codex_bot.redis.router.RedisRouter

---

## Protocols

### StreamStorageProtocol
::: codex_bot.redis.stream_processor.StreamStorageProtocol

### RetrySchedulerProtocol
::: codex_bot.redis.dispatcher.RetrySchedulerProtocol
