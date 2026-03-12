# 📦 Base

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

Модуль `base` определяет основные строительные блоки фреймворка `codex-bot`: иммутабельные DTO и абстрактный Оркестратор.

---

## 🧠 Почему так?

### Иммутабельность (Immutability)
Все DTO в `codex-bot` заморожены (`frozen=True`). В асинхронной среде `aiogram` передача мутабельных объектов между сервисами может привести к непредсказуемым состояниям гонки (race conditions). Иммутабельность гарантирует, что после создания объекта его нельзя изменить, что упрощает отладку и понимание системы.

### Stateless Оркестраторы
Оркестраторы — это сердце каждой фичи. Они спроектированы как **Stateless Singletons**. Это означает, что один экземпляр оркестратора обрабатывает запросы всех пользователей одновременно. Они не хранят данные пользователя в `self`. Весь контекст (user ID, chat ID, FSM state) передается через `Director` и `payload`.

---

## 🔄 Поток данных (The Flow)

1. **Вход:** Хендлер получает событие Telegram и извлекает `payload`.
2. **Обработка:** `Director` вызывает метод оркестратора `render_content(payload, director)`.
3. **Выход:** Оркестратор возвращает `ViewResultDTO` (текст + клавиатура).
4. **Сборка:** Базовый класс оборачивает результат в `UnifiedViewDTO`, обогащая его метаданными роутинга (chat_id, session_key).

---

## 💻 Пример реализации фичи

Каждая функциональная область бота (фича) начинается с создания своего оркестратора.

```python
from pydantic import BaseModel
from codex_bot.base.base_orchestrator import BaseBotOrchestrator
from codex_bot.base.view_dto import ViewResultDTO
from codex_bot.director import Director

# 1. Описываем данные, которые нужны для отрисовки экрана
class ProfilePayload(BaseModel):
    user_id: int
    is_premium: bool = False

# 2. Создаем оркестратор для фичи "Профиль"
class ProfileOrchestrator(BaseBotOrchestrator[ProfilePayload]):
    def __init__(self):
        # Указываем FSM-стейт, в который перейдет пользователь при входе в фичу
        super().__init__(expected_state="ProfileStates:main")

    async def render_content(
        self,
        payload: ProfilePayload,
        director: Director
    ) -> ViewResultDTO:
        # Логика получения данных (например, из БД)
        # Вся информация о пользователе доступна через director

        text = (
            f"👤 Профиль пользователя {payload.user_id}\n"
            f"Статус: {'Premium' if payload.is_premium else 'Обычный'}"
        )

        # Возвращаем текст и клавиатуру (опционально)
        return ViewResultDTO(
            text=text,
            kb=None # Здесь может быть InlineKeyboardMarkup
        )
```

---

## 🗺️ Карта модуля

| Компонент | Описание |
|:---|:---|
| **[📄 API Reference](../../../api/base.md)** | Технические детали `BaseBotOrchestrator` и DTO. |
| **[📄 View DTOs](../../../api/base.md#view-dtos)** | `UnifiedViewDTO`, `ViewResultDTO` и `MessageCoordsDTO`. |
| **[📄 Context DTO](../../../api/base.md#context-dto)** | `BaseBotContext` для нормализации данных события. |

---

**Последнее обновление:** 2025-03-09
