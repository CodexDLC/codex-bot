# 🧠 FSM

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

Модуль `fsm` обеспечивает продвинутое управление состоянием и автоматическую очистку UI (Garbage Collector) в фреймворке `codex-bot`.

---

## 🧠 Почему так?

### Изоляция данных (Namespacing)
В сложном боте несколько фич могут одновременно хранить временные данные (черновики) в FSM-хранилище пользователя. Без изоляции одна фича может случайно перезаписать данные другой. `BaseStateManager` решает это, используя **пространства имен** (например, `draft:booking`), гарантируя каждой фиче свою приватную область внутри общей FSM-сессии.

### Чистота чата (Garbage Collector)
Когда бот использует UI на основе инлайн-кнопок, пользователи часто отправляют случайные текстовые сообщения, которые засоряют чат и нарушают логику интерфейса. `GarbageCollector` автоматически удаляет такие нежелательные сообщения в определенных состояниях, сохраняя интерфейс чистым и сфокусированным на кнопках.

---

## 🔄 Поток данных (The Flow)

1. **Управление состоянием:** Оркестратор фичи использует `BaseStateManager` для `update()` или `get_payload()` из своего изолированного FSM-пространства.
2. **Регистрация:** При запуске `FeatureDiscoveryService` регистрирует «мусорные состояния» из каждой фичи в `GarbageStateRegistry`.
3. **Фильтрация:** Когда пользователь отправляет текстовое сообщение, `IsGarbageStateFilter` проверяет, зарегистрирован ли текущий FSM-стейт как «мусорный».
4. **Очистка:** Если стейт мусорный, `common_fsm_router` перехватывает сообщение и удаляет его из чата Telegram.

---

## 💻 Пример автоматической очистки UI

`GarbageStateRegistry` позволяет автоматически удалять текстовые сообщения пользователя в тех состояниях, где бот ожидает только нажатия кнопок.

```python
from codex_bot.fsm.garbage_collector import GarbageStateRegistry
from codex_bot.fsm.state_manager import BaseStateManager

# 1. Регистрируем состояния, в которых нужно удалять текстовый мусор
garbage_registry = GarbageStateRegistry()
garbage_registry.register_states([
    "BookingStates:main",
    "ProfileStates:edit_photo"
])

# 2. В хендлере (автоматически через RouterBuilder)
# Если пользователь напишет текст в стейте "BookingStates:main",
# бот просто удалит это сообщение, сохраняя интерфейс чистым.

# 3. Использование изолированного хранилища данных фичи
class BookingStateManager(BaseStateManager[BookingPayload]):
    namespace = "booking"

# В оркестраторе:
# state_manager = BookingStateManager(director.state)
# await state_manager.update(BookingPayload(service_id=42))
# data = await state_manager.get_payload() # Вернет только данные "booking"
```

---

## 🗺️ Карта модуля

| Компонент | Описание |
|:---|:---|
| **[📄 API Reference](../../../api/fsm.md)** | Технические детали `BaseStateManager` и `GarbageStateRegistry`. |
| **[📄 State Manager](../../../api/fsm.md#basestatemanager)** | Изолированное хранилище данных фичи внутри FSM. |
| **[📄 Garbage Collector](../../../api/fsm.md#garbagestateregistry)** | Автоматическое удаление нежелательных текстовых сообщений. |

---

**Последнее обновление:** 2025-03-09
