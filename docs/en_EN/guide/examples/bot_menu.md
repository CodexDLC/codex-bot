# 🚀 Full Feature Implementation Example (Menu/Dashboard)

[⬅️ Back to Best Practices](../best_practices.md)

This section provides the complete structure and implementation of a complex feature — the **Main Menu (Dashboard)**. This example demonstrates the standard for code organization in `codex-bot`.

---

## 🏗️ Recommended Feature Folder Structure

To maintain cleanliness and scalability, we recommend separating responsibilities within a feature as follows:

```text
📂 bot_menu/
    📄 __init__.py
    📄 feature_setting.py      # FSM states and feature metadata
    📂 contracts/              # Interfaces and protocols
        📄 menu_contract.py
    📂 handlers/               # Aiogram routers and handlers
        📄 menu_handlers.py
    📂 logic/                  # Business logic and navigation
        📄 orchestrator.py
    📂 resources/              # Static resources and data
        📄 callbacks.py        # CallbackData classes
        📄 dto.py              # Pydantic data models
        📄 keyboards.py        # Keyboard factories
        📄 texts.py            # Text formatters
    📂 ui/                     # Final view assembly
        📄 menu_ui.py          # Class for rendering ViewResultDTO
```

---

## 1. Contracts and Data (Contracts & DTO)

### `resources/callbacks.py`
```python
from aiogram.filters.callback_data import CallbackData

class DashboardCallback(CallbackData, prefix="dash"):
    action: str # open, select, refresh
    target: str | None = None # feature name or tab name
```

### `resources/dto.py`
```python
from codex_bot.base.context_dto import BaseBotContext

class MenuContext(BaseBotContext):
    """Context extended with menu-specific fields."""
    action: str
    target: str | None = None
```

---

## 2. Presentation (UI & Resources)

### `resources/keyboards.py`
```python
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

def build_dashboard_keyboard(buttons: dict, mode: str = "bot_menu"):
    i18n = I18nContext.get_current()
    builder = InlineKeyboardBuilder()

    # Sort buttons by priority and add to the keyboard
    sorted_btns = sorted(buttons.values(), key=lambda x: x.get("priority", 100))
    for btn in sorted_btns:
        callback = DashboardCallback(action="select", target=btn.get("key")).pack()
        builder.button(text=f"{btn.get('icon', '')} {btn.get('text')}", callback_data=callback)

    builder.adjust(2)
    return builder.as_markup()
```

### `ui/menu_ui.py`
```python
from codex_bot.base.view_dto import ViewResultDTO
from ..resources.keyboards import build_dashboard_keyboard

class BotMenuUI:
    """Responsible for rendering dashboard text and keyboard."""
    def render_dashboard(self, buttons: dict, mode: str = "bot_menu") -> ViewResultDTO:
        title = "📱 Main Menu"
        lines = [f"{b.get('icon')} <b>{b.get('text')}</b> — {b.get('description')}"
                 for b in sorted(buttons.values(), key=lambda x: x.get("priority", 100))]

        full_text = f"{title}\n\n" + "\n".join(lines)
        return ViewResultDTO(text=full_text, kb=build_dashboard_keyboard(buttons, mode))
```

---

## 3. Logic and Navigation (Logic & Orchestrator)

### `logic/orchestrator.py`
The orchestrator manages internal navigation (switching tabs) and external navigation (transitioning to other features via the `Director`).

```python
class BotMenuOrchestrator(BaseBotOrchestrator):
    def __init__(self, discovery_provider: MenuDiscoveryProvider, settings: BotSettings):
        super().__init__(expected_state=BotMenuStates.main)
        self.discovery = discovery_provider
        self.ui = BotMenuUI()

    async def handle_callback(self, director: Director, ctx: MenuContext) -> UnifiedViewDTO | None:
        if ctx.action == "select":
            return await self.handle_menu_click(director, target=ctx.target or "")
        return await self.render_dashboard(director)

    async def render_dashboard(self, director: Director, mode: str = "bot_menu") -> UnifiedViewDTO:
        is_admin_mode = mode == "dashboard_admin"

        # Access Control (RBAC)
        if is_admin_mode and not self._is_user_admin(director.user_id):
            return await self.render_dashboard(director, mode="bot_menu")

        available_features = self.discovery.get_menu_buttons(is_admin=is_admin_mode)
        menu_view = self.ui.render_dashboard(available_features, mode=mode)

        return UnifiedViewDTO(menu=menu_view, chat_id=director.chat_id, session_key=director.user_id)

    async def handle_menu_click(self, director: Director, target: str) -> UnifiedViewDTO | None:
        # 1. Internal navigation (switching menu tabs)
        if target in ["dashboard_admin", "bot_menu"]:
            return await self.render_dashboard(director, mode=target)

        # 2. External navigation (transitioning to another feature via Director)
        features_config = self.discovery.get_menu_buttons()
        target_config = features_config.get(target)

        if not target_config or not self._check_access(director.user_id, target_config):
            return None

        target_feature = target_config.get("target_state", target)
        return await director.set_scene(feature=target_feature, payload=None)

    def _is_user_admin(self, user_id: int) -> bool:
        return user_id in self.settings.owner_ids_list or user_id in self.settings.superuser_ids_list
```

---

## 4. Processing (Handlers)

### `handlers/menu_handlers.py`
```python
@router.callback_query(DashboardCallback.filter())
async def handle_dashboard_callback(call: CallbackQuery, callback_data: DashboardCallback,
                                   state: FSMContext, container: BotContainer):
    await call.answer()
    orchestrator = container.features.get("bot_menu")

    base_ctx = ContextHelper.extract_base_context(call)
    ctx = MenuContext(**base_ctx.model_dump(), action=callback_data.action, target=callback_data.target)

    director = Director(container=container, state=state, user_id=ctx.user_id,
                        chat_id=ctx.chat_id, trigger_id=call.message.message_id)

    view_dto = await orchestrator.handle_callback(director, ctx)
    if view_dto:
        await container.view_sender.send(view_dto)
```

---

## 💎 Key Patterns in this Example

1. **Stateless Approach**: The `director` is passed as an argument to every method. The orchestrator does not store user state, making it thread-safe.
2. **Navigation Separation**: The orchestrator clearly distinguishes between switching tabs within itself and transitioning to other features in the system.
3. **RBAC (Role Based Access Control)**: Permission check logic is encapsulated within the orchestrator, ensuring interface security.
4. **DI Container**: All dependencies (settings, menu providers) are injected via the constructor.

---
**Last Updated:** 2025-03-09
