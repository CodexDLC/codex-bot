# Task 007: SQLAlchemy Sender Storage

**Priority:** Medium
**Status:** Planned
**Category:** Persistence / Database

---

## 🎯 Goal
Implement a persistent UI coordinate storage based on SQLAlchemy (Async). This allows the ViewSender to work without Redis while still persisting message IDs between bot restarts.

## 🛠 Features
1. **Database Schema**: Create a simple table `codex_bot_sender_coords` with fields: `session_key`, `is_channel`, `menu_msg_id`, `content_msg_id`, and `updated_at`.
2. **SQLAlchemy Implementation**: Implement `SenderStateStorageProtocol` using async SQLAlchemy sessions.
3. **Upsert Logic**: Handle "create or update" operations atomically using database-specific upsert features (or a manual check).
4. **Integration**: Allow easy switching between Redis and Database storage in the BotBuilder.

---
[⬅️ Back to Roadmap](../../ru_RU/roadmap.md)
