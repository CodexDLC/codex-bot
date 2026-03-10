# 📤 Sender

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `sender` module provides a stateless service for sending and synchronizing the Telegram bot's UI in the `codex-bot` framework.

---

## 🧠 The Why

### UI Persistence
In a typical bot, every interaction sends a new message, creating a long and messy chat history. `ViewSender` solves this by managing two **persistent messages** (Menu and Content). Instead of sending new messages, it edits existing ones whenever possible, keeping the chat clean and focused.

### Stateless Delivery
Since `ViewSender` is a **Stateless Singleton**, it doesn't store any user-specific data in `self`. It uses a `SenderManager` to retrieve the current message IDs (coordinates) from a persistent storage (e.g., Redis) for each request. This ensures that the UI remains consistent even across multiple bot instances.

---

## 🔄 The Flow

1. **Input:** The `Director` calls the Orchestrator, which returns a `UnifiedViewDTO`.
2. **Coordination:** The `ViewSender` receives the `UnifiedViewDTO` and retrieves the current `menu_msg_id` and `content_msg_id` from the `SenderManager`.
3. **Synchronization:**
    - **Deletion:** If `trigger_message_id` is present (e.g., `/start`), it is deleted.
    - **Editing:** If the messages exist, `ViewSender` edits them with the new content and keyboard.
    - **Creation:** If they don't exist, new messages are sent.
4. **Persistence:** The `SenderManager` updates the message IDs in the storage for the next request.

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/sender.md)** | Technical details for `ViewSender` and `SenderManager`. |
| **[📄 Sender Keys](../../../api/sender.md#senderkeys)** | Key factory for UI coordinate storage. |
| **[📄 Protocols](../../../api/sender.md#protocols)** | `SenderStateStorageProtocol` for UI coordinate storage. |

---

**Last Updated:** 2025-02-07
