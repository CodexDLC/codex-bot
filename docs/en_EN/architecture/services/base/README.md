# Base Orchestrator — The Heart of a Feature

**BaseBotOrchestrator** is an abstract base class for implementing business logic. Every feature in your bot must have its own orchestrator.

---

## 🏛 Stateless Principle
Orchestrators are singletons (one instance per application). They **must not store user data** in `self`. All request context is passed via the `director` argument.

---

## ✍️ Method Signatures

We use a unified argument order: the context (`director`) always comes first, followed by the `payload`.

### render_content (Required)
The main method for rendering content.

```python
async def render_content(
    self,
    director: Director,
    payload: dict | None = None
) -> ViewResultDTO | UnifiedViewDTO:
    # Your business logic lives here
    return ViewResultDTO(text="Hello", kb=...)
```

---

## 🔄 Request Lifecycle

1.  **Director** calls `handle_entry`.
2.  `handle_entry` calls `render`.
3.  `render` calls your `render_content` implementation.
4.  The framework automatically wraps the result into a `UnifiedViewDTO` and passes it back to the Director for session metadata enrichment.

---

## 💡 Type Safety
Always specify the `PayloadT` type when inheriting, so the IDE can provide autocomplete for fields within `render_content`:

```python
class MyOrchestrator(BaseBotOrchestrator[MyDataDTO]):
    ...
```
