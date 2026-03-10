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

## 💻 UI Garbage Collection Example

`GarbageStateRegistry` allows you to automatically delete unwanted text messages in states where the bot only expects button clicks.

```python
from codex_bot.fsm.garbage_collector import GarbageStateRegistry
from codex_bot.fsm.state_manager import BaseStateManager

# 1. Register states where text garbage should be deleted
garbage_registry = GarbageStateRegistry()
garbage_registry.register_states([
    "BookingStates:main",
    "ProfileStates:edit_photo"
])

# 2. In the handler (automatically via RouterBuilder)
# If a user writes text in the "BookingStates:main" state,
# the bot will simply delete that message, keeping the interface clean.

# 3. Using isolated feature data storage
class BookingStateManager(BaseStateManager[BookingPayload]):
    namespace = "booking"

# In the orchestrator:
# state_manager = BookingStateManager(director.state)
# await state_manager.update(BookingPayload(service_id=42))
# data = await state_manager.get_payload() # Returns only "booking" data
```

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/fsm.md)** | Technical details for `BaseStateManager` and `GarbageStateRegistry`. |
| **[📄 State Manager](../../../api/fsm.md#basestatemanager)** | Isolated feature data storage within FSM. |
| **[📄 Garbage Collector](../../../api/fsm.md#garbagestateregistry)** | Automatic deletion of unwanted text messages. |

---

**Last Updated:** 2025-03-09
