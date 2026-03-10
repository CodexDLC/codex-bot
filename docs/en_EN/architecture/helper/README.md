# 🧰 Helper

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `helper` module provides utility helpers for extracting context and normalizing data from Telegram events in the `codex-bot` framework.

---

## 🧠 The Why

### Context Normalization
In `aiogram`, different event types (e.g., `Message`, `CallbackQuery`) have different structures for accessing the user ID, chat ID, and message ID. `ContextHelper` provides a unified way to extract this data into an immutable `BaseBotContext`. This ensures that your business logic doesn't need to know the specific type of event it's handling.

### Channel & Group Support
In some cases (e.g., posts in a channel), the `from_user` field might be missing. `ContextHelper` handles these edge cases by providing a fallback (e.g., using `chat_id` as the `user_id`), ensuring that the bot's session management remains consistent across all chat types.

---

## 🔄 The Flow

1. **Extraction:** A handler receives a `Message` or `CallbackQuery` and calls `ContextHelper.extract_base_context(event)`.
2. **Normalization:** The helper identifies the event type and extracts the `user_id`, `chat_id`, `message_id`, and `thread_id`.
3. **Fallback:** If `from_user` is missing, the `chat_id` is used as the `user_id` for session uniqueness.
4. **Creation:** An immutable `BaseBotContext` is returned, ready to be used by the `Director` or Orchestrator.

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/helper.md)** | Technical details for `ContextHelper`. |
| **[📄 Context Helper](../../../api/helper.md#contexthelper)** | Extraction of `BaseBotContext` from Telegram events. |

---

**Last Updated:** 2025-02-07
