# 🧭 Director

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `director` module acts as the central coordinator for cross-feature transitions in the `codex-bot` framework.

---

## 🧠 The Why

### Decoupling Features
In a large bot, features often need to transition from one to another (e.g., from "Profile" to "Booking"). Without a central coordinator, features would need to import each other, creating circular dependencies and making the system brittle. The `Director` solves this by using a **DI-container** and **Protocols** to decouple features.

### Stateless Context
Since Orchestrators are stateless, they need a way to access the current request's context (user ID, chat ID, FSM state). The `Director` is instantiated on every incoming request and passes itself as an argument to the Orchestrator's methods. This ensures that all user-specific data is isolated within the `Director` instance.

---

## 🔄 The Flow

1. **Initialization:** A handler creates a `Director` instance with the current `FSMContext`, `user_id`, and `chat_id`.
2. **Transition:** The handler calls `director.set_scene(feature="booking", payload=...)`.
3. **Discovery:** The `Director` retrieves the requested Orchestrator from the DI-container's `features` registry.
4. **State Change:** If the Orchestrator has an `expected_state`, the `Director` automatically sets the user's FSM state.
5. **Execution:** The `Director` calls the Orchestrator's `handle_entry(director=self, payload=...)` method.
6. **Enrichment:** The `Director` enriches the resulting `UnifiedViewDTO` with routing metadata before returning it.

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/director.md)** | Technical details for the `Director` class. |
| **[📄 Protocols](../../../api/director.md#protocols)** | `OrchestratorProtocol`, `ContainerProtocol`, and `SceneConfig`. |

---

**Last Updated:** 2025-02-07
