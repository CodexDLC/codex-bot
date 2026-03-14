# ViewSender — UI Management

**ViewSender** is responsible for delivering the UI to the user and synchronizing messages. It creates an SPA (Single Page Application) feel within Telegram.

---

## 🏗 How it Works
The service manages two persistent bot messages:
1.  **Menu** — The navigation block at the top.
2.  **Content** — The main information block.

Instead of sending new messages for every click, ViewSender **edits** existing ones, storing their IDs in a database (coordinates).

---

## 🔒 Group Isolation
ViewSender automatically detects the chat type:
*   **Private Chats**: Coordinates are bound to the `user_id`.
*   **Groups & Topics**: Coordinates are bound to the `chat_id` or `thread_id`. This prevents interface conflicts when different users interact with the bot in the same group.

---

## 🔋 Storages
Two storage modes are supported for message IDs:
1.  **Redis (Production)**: Persists the interface even after bot restarts. Uses high-performance Redis Hashes.
2.  **In-Memory (Dev)**: Stores data in RAM. Ideal for development without a Redis instance.

---

## 🧹 Garbage Collection
Together with the `GarbageStateRegistry`, ViewSender can automatically delete old messages and keyboards during transitions between logical blocks, keeping the chat history clean.
