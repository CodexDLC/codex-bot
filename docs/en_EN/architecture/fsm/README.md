# 🧠 FSM

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `fsm` module provides advanced state management and automatic UI cleanup (Garbage Collector) for the `codex-bot` framework.

---

## 🧠 The Why

### Data Isolation (Namespacing)
In a complex bot, multiple features might need to store temporary data (drafts) in the user's FSM storage. Without isolation, one feature could accidentally overwrite another's data. `BaseStateManager` solves this by using **namespaced keys** (e.g., `draft:booking`), ensuring each feature has its own private storage area within the global FSM session.

### Chat Cleanliness (Garbage Collector)
When a bot uses an inline-button-based UI, users often send accidental text messages that clutter the chat and break the flow. The `GarbageCollector` automatically deletes these unwanted messages in specific states, keeping the interface clean and focused on the buttons.

---

## 🔄 The Flow

1. **State Management:** A feature's Orchestrator uses `BaseStateManager` to `update()` or `get_payload()` from its isolated FSM namespace.
2. **Registration:** During startup, `FeatureDiscoveryService` registers "garbage states" from each feature into the `GarbageStateRegistry`.
3. **Filtering:** When a user sends a text message, the `IsGarbageStateFilter` checks if the current FSM state is registered as "garbage".
4. **Cleanup:** If it is, the `common_fsm_router` catches the message and deletes it from the Telegram chat.

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/fsm.md)** | Technical details for `BaseStateManager` and `GarbageStateRegistry`. |
| **[📄 State Manager](../../../api/fsm.md#basestatemanager)** | Isolated feature data storage within FSM. |
| **[📄 Garbage Collector](../../../api/fsm.md#garbagestateregistry)** | Automatic deletion of unwanted text messages. |

---

**Last Updated:** 2025-02-07
