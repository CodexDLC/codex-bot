# 🔄 Redis

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

Модуль `redis` обеспечивает надежную интеграцию с Redis Streams для фоновой обработки и событийно-ориентированной архитектуры в фреймворке `codex-bot`.

---

## 🧠 Почему так?

### Событийно-ориентированная архитектура (Event-Driven)
В большом боте некоторые действия (например, отправка уведомлений, обработка платежей) должны происходить в фоне, не блокируя основной цикл поллинга Telegram. Redis Streams предоставляют надежный способ развязки этих действий от UI-логики бота.

### Надежность (Consumer Groups)
`RedisStreamProcessor` использует **Redis Consumer Groups** для гарантии того, что каждое сообщение будет обработано хотя бы один раз. Он поддерживает автоматическое подтверждение (ACK) и планирование повторных попыток (через `RetrySchedulerProtocol`), делая систему устойчивой к сбоям и сетевым проблемам.

---

## 🔄 Поток данных (The Flow)

1. **Производство:** Внешний сервис или другая фича бота добавляет сообщение в Redis Stream (например, `bot_events`).
2. **Потребление:** `RedisStreamProcessor` опрашивает стрим через Consumer Group и читает порцию сообщений.
3. **Диспетчеризация:** `BotRedisDispatcher` получает сообщение и находит подходящий хендлер на основе поля `type` в payload.
4. **Исполнение:** Хендлер (например, `on_booking_confirmed`) вызывается с DI-контейнером проекта.
5. **Подтверждение:** Если хендлер успешен, процессор отправляет `XACK` в Redis. Если нет — сообщение планируется для повторной попытки.

---

## 💻 Пример работы с Redis Streams

Использование Redis Streams позволяет обрабатывать фоновые события (например, уведомления от бэкенда) асинхронно.

```python
from codex_bot.redis.router import RedisRouter
from codex_bot.redis.dispatcher import BotRedisDispatcher
from codex_bot.redis.stream_processor import RedisStreamProcessor

# 1. Создаем роутер для событий Redis
redis_router = RedisRouter()

# 2. Регистрируем хендлер для типа события "order_created"
@redis_router.on_event("order_created")
async def on_order_created(payload: dict, container: MyContainer):
    # Логика обработки события (например, отправка сообщения пользователю)
    user_id = payload["user_id"]
    await container.sender.send_text(user_id, "✅ Ваш заказ создан!")

# 3. Настраиваем процессор стрима
processor = RedisStreamProcessor(
    redis=redis_client,
    stream_name="bot_events",
    group_name="bot_service",
    consumer_name="worker_1",
    dispatcher=BotRedisDispatcher(router=redis_router, container=my_container)
)

# 4. Запускаем в основном цикле
# asyncio.create_task(processor.run())
```

---

## 🗺️ Карта модуля

| Компонент | Описание |
|:---|:---|
| **[📄 API Reference](../../../api/redis.md)** | Технические детали `RedisRouter` и `BotRedisDispatcher`. |
| **[📄 Stream Processor](../../../api/redis.md#redisstreamprocessor)** | Цикл опроса Redis Stream (Consumer Group). |
| **[📄 Dispatcher](../../../api/redis.md#botredisdispatcher)** | Диспетчер сообщений Redis Stream для бота. |
| **[📄 Protocols](../../../api/redis.md#protocols)** | `RetrySchedulerProtocol` и `StreamStorageProtocol`. |

---

**Последнее обновление:** 2025-03-09
