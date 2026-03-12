# 🧭 Director

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `director` module acts as the central coordinator for cross-feature transitions in the `codex-bot` framework.

---

## 🧠 Why this way?

### Feature Decoupling
In a large bot, features often need to transition from one to another (e.g., from "Profile" to "Booking"). Without a central coordinator, features would have to import each other, creating circular dependencies. The `Director` solves this by using a **DI container** and **Protocols** to decouple features.

### Stateless Context
Since orchestrators do not store state, they need a way to access the context of the current request (user ID, chat ID, FSM state). The `Director` is instantiated for each incoming request and passes itself as an argument to orchestrator methods. This ensures user data isolation within the `Director` instance.

---

## 🔄 The Flow

1. **Initialization:** The handler creates a `Director` instance with the current `FSMContext`, `user_id`, and `chat_id`.
2. **Transition:** The handler calls `director.set_scene(feature="booking", payload=...)`.
3. **Lookup:** The `Director` retrieves the required orchestrator from the `features` registry of the DI container.
4. **State Change:** If the orchestrator has declared an `expected_state`, the `Director` automatically sets the user's FSM state.
5. **Execution:** The `Director` calls the orchestrator's `handle_entry(director=self, payload=...)` method.
6. **Enrichment:** The `Director` enriches the `UnifiedViewDTO` result with routing metadata before returning it.

---

## 💻 Usage Example

In a typical scenario, the `Director` is used inside an Aiogram handler to switch the user to a new functional area (feature).

```python
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from codex_bot.director import Director
from codex_bot.sender.view_sender import ViewSender

router = Router()

@router.callback_query(F.data == "start_booking")
async def on_booking_click(
    callback: CallbackQuery,
    state: FSMContext,
    container: MyContainer, # Your DI container
    sender: ViewSender      # View sending service
):
    # 1. Initialize Director for the current request
    director = Director(
        container=container,
        state=state,
        user_id=callback.from_user.id,
        chat_id=callback.message.chat.id,
        trigger_id=callback.message.message_id # For deleting the old message
    )

    # 2. Switch scene to "booking"
    # The Director will find the BookingOrchestrator in the container,
    # set the required FSM state, and trigger the rendering logic.
    view = await director.set_scene(
        feature="booking",
        payload={"service_id": 42} # Data for feature initialization
    )

    # 3. Send the result to the user
    if view:
        await sender.send(view)
```

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/director.md)** | Technical details of the `Director` class. |
| **[📄 Protocols](../../../api/director.md#protocols)** | `OrchestratorProtocol`, `ContainerProtocol`, and `SceneConfig`. |

---

**Last Updated:** 2025-03-09
