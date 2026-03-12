# 🚀 Полный пример реализации фичи (Меню/Дашборд)

[⬅️ Назад к списку гайдов](../best_practices.md)

В этом разделе приведена полная структура и реализация сложной фичи — **Главного меню (Дашборда)**. Этот пример демонстрирует стандарт организации кода в `codex-bot`.

---

## 🏗️ Рекомендуемая структура папок фичи

Для поддержания чистоты и масштабируемости мы рекомендуем разделять ответственность внутри фичи следующим образом:

```text
📂 bot_menu/
    📄 __init__.py
    📄 feature_setting.py      # Состояния FSM и метаданные фичи
    📂 contracts/              # Интерфейсы и протоколы
        📄 menu_contract.py
    📂 handlers/               # Aiogram роутеры и обработчики
        📄 menu_handlers.py
    📂 logic/                  # Бизнес-логика и навигация
        📄 orchestrator.py
    📂 resources/              # Статические ресурсы и данные
        📄 callbacks.py        # CallbackData классы
        📄 dto.py              # Pydantic модели данных
        📄 keyboards.py        # Фабрики клавиатур
        📄 texts.py            # Форматтеры текстов
    📂 ui/                     # Сборка финального представления
        📄 menu_ui.py          # Класс для рендеринга ViewResultDTO
```

---

## 1. Контракты и Данные (Contracts & DTO)

### `resources/callbacks.py`
```python
from aiogram.filters.callback_data import CallbackData

class DashboardCallback(CallbackData, prefix="dash"):
    action: str # open, select, refresh
    target: str | None = None # имя фичи или вкладки
```

### `resources/dto.py`
```python
from codex_bot.base.context_dto import BaseBotContext

class MenuContext(BaseBotContext):
    """Контекст, расширенный специфичными для меню полями."""
    action: str
    target: str | None = None
```

---

## 2. Презентация (UI & Resources)

### `resources/keyboards.py`
```python
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_i18n import I18nContext

def build_dashboard_keyboard(buttons: dict, mode: str = "bot_menu"):
    i18n = I18nContext.get_current()
    builder = InlineKeyboardBuilder()

    # Сортируем кнопки по приоритету и добавляем в клавиатуру
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
    """Отвечает за рендеринг текста и клавиатуры дашборда."""
    def render_dashboard(self, buttons: dict, mode: str = "bot_menu") -> ViewResultDTO:
        title = "📱 Главное меню"
        lines = [f"{b.get('icon')} <b>{b.get('text')}</b> — {b.get('description')}"
                 for b in sorted(buttons.values(), key=lambda x: x.get("priority", 100))]

        full_text = f"{title}\n\n" + "\n".join(lines)
        return ViewResultDTO(text=full_text, kb=build_dashboard_keyboard(buttons, mode))
```

---

## 3. Логика и Навигация (Logic & Orchestrator)

### `logic/orchestrator.py`
Оркестратор управляет внутренней навигацией (смена вкладок) и внешней (переход в другие фичи через `Director`).

```python
class BotMenuOrchestrator(BaseBotOrchestrator):
    def __init__(self, discovery_provider: MenuDiscoveryProvider, settings: BotSettings):
        super().__init__(expected_state=BotMenuStates.main)
        self.discovery = discovery_provider
        self.settings = settings
        self.ui = BotMenuUI()

    async def handle_callback(self, director: Director, ctx: MenuContext) -> UnifiedViewDTO | None:
        if ctx.action == "select":
            return await self.handle_menu_click(director, target=ctx.target or "")
        return await self.render_dashboard(director)

    async def render_dashboard(self, director: Director, mode: str = "bot_menu") -> UnifiedViewDTO:
        is_admin_mode = mode == "dashboard_admin"

        # Контроль доступа (RBAC)
        if is_admin_mode and not self._is_user_admin(director.user_id):
            return await self.render_dashboard(director, mode="bot_menu")

        available_features = self.discovery.get_menu_buttons(is_admin=is_admin_mode)
        menu_view = self.ui.render_dashboard(available_features, mode=mode)

        return UnifiedViewDTO(menu=menu_view, chat_id=director.chat_id, session_key=director.user_id)

    async def handle_menu_click(self, director: Director, target: str) -> UnifiedViewDTO | None:
        # 1. Внутренняя навигация (переключение вкладок меню)
        if target in ["dashboard_admin", "bot_menu"]:
            return await self.render_dashboard(director, mode=target)

        # 2. Внешняя навигация (переход в другую фичу через Director)
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

## 4. Обработка (Handlers)

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

## 💎 Ключевые паттерны в этом примере

1. **Stateless подход**: `director` передается как аргумент в каждый метод. Оркестратор не хранит состояние пользователя, что делает его потокобезопасным.
2. **Разделение навигации**: Оркестратор четко разделяет переключение вкладок внутри себя и переходы в другие фичи системы.
3. **RBAC (Role Based Access Control)**: Логика проверки прав инкапсулирована в оркестраторе, что гарантирует безопасность интерфейса.
4. **DI-контейнер**: Все зависимости (настройки, провайдеры меню) инжектируются через конструктор.

---
**Последнее обновление:** 2025-03-09
