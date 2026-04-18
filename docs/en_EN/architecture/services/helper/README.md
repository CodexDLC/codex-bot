# Helper Tools

Helpers in **codex-bot** are a set of utilities designed to simplify common tasks: working with identifiers, safe FSM operations, and normalizing request context.

We distinguish between **Public** helpers (for use in your code) and **Internal** helpers (used by the library's core).

---

## 🛠 Public Helpers (Public API)

These tools can be imported and used within your handlers or orchestrators.

### 1. ID Inspector (`codex_bot.helper.id_inspector`)
A utility for quickly retrieving technical data of the current context (User ID, Chat ID, Thread ID).
- **Application**: Debugging, configuring access rights, finding channel IDs.
- **Usage**:
```python
from codex_bot.helper.id_inspector import inspect_ids_handler
router.message(Command("id"))(inspect_ids_handler)
```

### 2. State Helper (`codex_bot.fsm.state_helper`)
A low-level wrapper over aiogram FSM for safe atomic operations.
- **Application**: Working with FSM outside of the standard `BaseStateManager`.
- **Features**: Automatically removes keys from Redis if the value is `None` (protection against "zombie dictionaries").

---

## 🔒 Internal Helpers (Internal)

These tools are used by the library core (e.g., the Director), but you can also access them if deep customization is required.

### 1. Context Helper (`codex_bot.helper.context_helper`)
Responsible for normalizing data from different event types (Message, CallbackQuery, or dict).
- **Task**: Transform any event into a `BaseBotContext` object with a unified set of IDs.
- **Application**: Used in Middleware to prepare data for the Director.

---

## 🧭 Related Components
- **[Director](../director/README.md)** — Uses `ContextHelper` for initialization.
- **[FSM](../fsm/README.md)** — Uses `StateHelper` for data management in Redis.
