# Redis Stream Infrastructure

**codex-bot** features a robust subsystem for asynchronous event processing via **Redis Streams**. This allows the bot to react to external signals and perform heavy tasks in the background without blocking the main aiogram thread.

---

## 🏗 Key Components

Stream processing is built on three levels:
1. **RedisStreamProcessor**: Infinite loop for reading messages.
2. **BotRedisDispatcher**: Hub for event distribution.
3. **RedisRouter**: Modular registration of event handlers.

---

## 🚀 Future: Remote State Control

We plan to add support for navigation keys directly within the Redis **payload**.

**Concept:**
If a backend sends a message like:
`{"user_id": 123, "__next_scene__": "battle_results"}`

The bot will automatically switch the user to the specified scene.

---

## ⚠️ Current Limitations

1. **Container instead of Director**: In the current version, only the `container` is passed to handlers.
2. **Manual FSM Management**: Use `container.storage` directly with the `user_id` key.

---

## 🧭 Related Components
- **[ViewSender](../view_sender/README.md)** — Sending notifications after stream processing.
- **[Task 004](../../../tasks/004_high_redis_fsm_integration.md)** — Implementation details.
