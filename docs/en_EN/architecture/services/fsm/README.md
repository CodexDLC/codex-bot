# State Management (FSM)

In **codex-bot**, working with FSM (Finite State Machine) is based on the principle of strict data isolation. We use **Namespacing** to ensure that features do not conflict with each other.

---

## 🏛 BaseStateManager

`BaseStateManager` is the base class for managing data for a specific feature. It isolates data under the `draft:<feature_key>` key within the user's general storage.

### Why is it needed?
1. **Safety**: The "Profile" feature will never overwrite temporary data from the "Booking" feature.
2. **Cleanliness**: You always know which part of the data belongs to which feature.
3. **Performance**: When clearing feature data (`clear()`), only its specific key is deleted, without affecting the rest of the user's state.

---

## ✍️ How to Use (Example)

Typically, for each feature, you create its own state manager inherited from `BaseStateManager`.

### 1. Creating a Custom Manager:
```python
from codex_bot.fsm.state_manager import BaseStateManager

class BookingStateManager(BaseStateManager):
    def __init__(self, state):
        # Pass the unique feature key
        super().__init__(state, feature_key="booking")

    async def save_hotel(self, hotel_id: int):
        await self.update(hotel_id=hotel_id)

    async def get_hotel(self) -> int | None:
        return await self.get_value("hotel_id")
```

### 2. Using it in an Orchestrator:
```python
async def render_content(self, payload, director: Director):
    # Create the manager, passing director.state to it
    fsm = BookingStateManager(director.state)

    # Read or update the data
    hotel_id = await fsm.get_hotel()
    ...
```

---

## 🔄 FSM in Telegram vs Redis/Webhooks

This is a key architectural difference in state access:

### 1. Telegram Features (User-Driven)
When a user interacts with the bot in a chat, we have a live `FSMContext`. We work through `BaseStateManager` and `director.state`.

### 2. External Events (Redis Streams / Webhooks)
Events from outside arrive asynchronously. At this moment, we **do not have an active `FSMContext`**, as the user session was not initiated from a chat.

- **Logic**: If an external service needs to change a user's state (e.g., switch them to the "Payment Successful" screen), it must access the storage directly via `container.storage`, using the `user_id` from the event data.
- **Scenario**: "Catch event -> Find user -> Update their state in Redis -> Send a push via ViewSender."

---

## 🚮 Garbage Collector (UI Cleanup)

`GarbageStateRegistry` uses FSM to track "junk" messages. The bot automatically deletes old keyboards and temporary notifications when the user changes states, keeping the chat clean.

---

## 🧭 Related Components
- **[Director](../director/README.md)** — bridge to `FSMContext` in Telegram features.
- **[ViewSender](../view_sender/README.md)** — uses FSM data to locate message IDs for updates.
