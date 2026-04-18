# Task 004: Redis Stream FSM Integration

**Priority:** High
**Status:** Planned
**Category:** Infrastructure / Redis

---

## 🎯 Goal
Enable direct access to user FSM states within Redis Stream handlers. This allows background events to trigger state changes and UI updates seamlessly.

## 🛠 Problem Statement
Currently, Redis handlers only receive raw `payload` and `container`. To change a user's state, developers must manually interact with Redis storage.

## 🚀 Proposed Solution
1. **Context Building**: Update `BotRedisDispatcher` to look for a `user_id` (and optional `chat_id`) in the incoming Redis message payload.
2. **Async Director**: If IDs are present, the dispatcher will automatically instantiate an `FSMContext` and a `Director` object.
3. **Handler Injection**: Allow Redis handlers to accept `director: Director` as an argument, providing the same API as regular Telegram handlers.

## ✅ Definition of Done
- Redis handlers can perform `await director.set_scene()`.
- `BaseStateManager` works inside Redis handlers.
- Documented convention for the `user_id` key in Redis payloads.
