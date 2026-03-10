# 📦 Base

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `base` module defines the core building blocks of the `codex-bot` framework: immutable Data Transfer Objects (DTOs) and the abstract Orchestrator.

---

## 🧠 The Why

### Immutability
All DTOs in `codex-bot` are **frozen** (using Pydantic's `frozen=True`). In an asynchronous environment like `aiogram`, passing mutable objects between services can lead to unpredictable race conditions. Immutability ensures that once a view or context is created, it cannot be modified, making the system easier to debug and reason about.

### Stateless Orchestrators
Orchestrators are the heart of every feature. They are designed as **Stateless Singletons**. This means a single instance of an orchestrator handles requests for all users concurrently. They do not store any user-specific data in `self`. All necessary context (user ID, chat ID, FSM state) is passed through the `Director` and the `payload`.

---

## 🔄 The Flow

1. **Input:** A handler receives a Telegram event and extracts a `payload`.
2. **Processing:** The `Director` calls the Orchestrator's `render_content(payload, director)` method.
3. **Output:** The Orchestrator returns a `ViewResultDTO` (text + keyboard).
4. **Assembly:** The base class wraps the result into a `UnifiedViewDTO`, enriching it with routing metadata (chat_id, session_key).

---

## 💻 Feature Implementation Example

Every functional area of the bot (feature) starts with creating its own orchestrator.

```python
from pydantic import BaseModel
from codex_bot.base.base_orchestrator import BaseBotOrchestrator
from codex_bot.base.view_dto import ViewResultDTO
from codex_bot.director import Director

# 1. Define the data needed for rendering the screen
class ProfilePayload(BaseModel):
    user_id: int
    is_premium: bool = False

# 2. Create an orchestrator for the "Profile" feature
class ProfileOrchestrator(BaseBotOrchestrator[ProfilePayload]):
    def __init__(self):
        # Specify the FSM state the user will transition to upon entering the feature
        super().__init__(expected_state="ProfileStates:main")

    async def render_content(
        self,
        payload: ProfilePayload,
        director: Director
    ) -> ViewResultDTO:
        # Logic for retrieving data (e.g., from a database)
        # All user information is available through the director

        text = (
            f"👤 User Profile {payload.user_id}\n"
            f"Status: {'Premium' if payload.is_premium else 'Regular'}"
        )

        # Return text and keyboard (optional)
        return ViewResultDTO(
            text=text,
            kb=None # This could be an InlineKeyboardMarkup
        )
```

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 API Reference](../../../api/base.md)** | Technical details for `BaseBotOrchestrator` and DTOs. |
| **[📄 View DTOs](../../../api/base.md#view-dtos)** | `UnifiedViewDTO`, `ViewResultDTO`, and `MessageCoordsDTO`. |
| **[📄 Context DTO](../../../api/base.md#context-dto)** | `BaseBotContext` for event data normalization. |

---

**Last Updated:** 2025-03-09
