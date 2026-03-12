# 🔄 Redis

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `redis` module provides robust integration with Redis Streams for background processing and event-driven architecture in the `codex-bot` framework.

---

## 🧠 The Why

### Event-Driven Architecture
In a large bot, some actions (e.g., sending notifications, processing payments) should happen in the background without blocking the main Telegram polling loop. Redis Streams provide a reliable way to decouple these actions from the bot's UI logic.

### Reliability (Consumer Groups)
The `RedisStreamProcessor` uses **Redis Consumer Groups** to ensure that every message is processed at least once. It supports automatic acknowledgment (ACK) and retry scheduling (via `RetrySchedulerProtocol`), making the system resilient to crashes and network issues.

---

## 🔄 The Flow

1. **Production:** An external service or another bot feature adds a message to a Redis Stream (e.g., `bot_events`).
2. **Consumption:** `RedisStreamProcessor` polls the stream using a Consumer Group and reads a batch of messages.
3. **Dispatching:** `BotRedisDispatcher` receives the message and finds the appropriate handler based on the `type` field in the payload.
4. **Execution:** The handler (e.g., `on_booking_confirmed`) is called with the project's DI-container.
5. **Acknowledgment:** If the handler succeeds, the processor sends an `XACK` to Redis. If it fails, the message is rescheduled for retry.

---

## 💻 Redis Streams Example

Using Redis Streams allows you to handle background events (e.g., notifications from a backend) asynchronously.

```python
from codex_bot.redis.router import RedisRouter
from codex_bot.redis.dispatcher import BotRedisDispatcher
from codex_bot.redis.stream_processor import RedisStreamProcessor

# 1. Create a router for Redis events
redis_router = RedisRouter()

# 2. Register a handler for the "order_created" event type
@redis_router.on_event("order_created")
async def on_order_created(payload: dict, container: MyContainer):
    # Logic for handling the event (e.g., sending a message to the user)
    user_id = payload["user_id"]
    await container.sender.send_text(user_id, "✅ Your order has been created!")

# 3. Configure the stream processor
processor = RedisStreamProcessor(
    redis=redis_client,
    stream_name="bot_events",
    group_name="bot_service",
    consumer_name="worker_1",
    dispatcher=BotRedisDispatcher(router=redis_router, container=my_container)
)

# 4. Run in the main loop
# asyncio.create_task(processor.run())
```

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/redis.md)** | Technical details for `RedisRouter` and `BotRedisDispatcher`. |
| **[📄 Stream Processor](../../../api/redis.md#redisstreamprocessor)** | Redis Stream polling loop (Consumer Group). |
| **[📄 Dispatcher](../../../api/redis.md#botredisdispatcher)** | Redis Stream message dispatcher for the bot. |
| **[📄 Protocols](../../../api/redis.md#protocols)** | `RetrySchedulerProtocol` and `StreamStorageProtocol`. |

---

**Last Updated:** 2025-03-09
