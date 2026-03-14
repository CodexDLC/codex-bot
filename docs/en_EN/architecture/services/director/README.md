# Director — Navigation Coordinator

The **Director** is the central hub for managing transitions between features. It is instantiated per request and encapsulates the full context (user_id, chat_id, FSM state).

---

## 🧠 Smart Resolver (Metadata Navigation)

This is a "killer feature" of the framework. The `director.resolve(data)` method allows the bot to automatically switch screens based on metadata received from an external source (API or DB).

**How it works:**
If your backend returns a response containing the `__next_scene__` (or `next_scene`) key, the Director will automatically perform a transition to that feature.

```python
async def render_content(self, director: Director, payload: Any):
    # Backend might return: {"meta": {"__next_scene__": "banned"}, "payload": {...}}
    raw_data = await director.container.api.get_user(director.user_id)

    # The Director handles the redirect logic automatically
    data = await director.resolve(raw_data)

    if isinstance(data, UnifiedViewDTO):
        return data # Seamless transition to the "banned" screen

    return self.ui.render_profile(data)
```

---

## 🚀 The set_scene Method

The primary method for manual context switching.

1.  **State Management**: Changes the FSM state idempotently (only if it differs from the current one).
2.  **Orchestrator Invocation**: Finds the target feature in the container and calls its `handle_entry`.
3.  **Enrichment**: Automatically injects `chat_id` and `session_key` into the resulting `UnifiedViewDTO`.

```python
# Transition to the booking feature from anywhere
view = await director.set_scene("booking", payload={"room_id": 101})
```

---

## 🛠 Protocols
The Director operates via `OrchestratorProtocol`, allowing it to interact with any object that implements this interface, keeping the system decoupled and flexible.
