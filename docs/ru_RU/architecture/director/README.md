# 🧭 Director

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

Модуль `director` выступает центральным координатором межфичевых переходов в фреймворке `codex-bot`.

---

## 🧠 Почему так?

### Развязка фич (Decoupling)
В большом боте фичам часто нужно переходить от одной к другой (например, из «Профиля» в «Бронирование»). Без центрального координатора фичи должны были бы импортировать друг друга, создавая циклические зависимости. `Director` решает это, используя **DI-контейнер** и **Протоколы** для развязки фич.

### Stateless Контекст
Поскольку оркестраторы не хранят состояние, им нужен способ доступа к контексту текущего запроса (user ID, chat ID, FSM state). `Director` инстанцируется на каждый входящий запрос и передает себя как аргумент в методы оркестратора. Это гарантирует изоляцию данных пользователя внутри экземпляра `Director`.

---

## 🔄 Поток данных (The Flow)

1. **Инициализация:** Хендлер создает экземпляр `Director` с текущим `FSMContext`, `user_id` и `chat_id`.
2. **Переход:** Хендлер вызывает `director.set_scene(feature="booking", payload=...)`.
3. **Поиск:** `Director` получает нужный оркестратор из реестра `features` DI-контейнера.
4. **Смена состояния:** Если оркестратор объявил `expected_state`, `Director` автоматически устанавливает FSM-стейт пользователя.
5. **Исполнение:** `Director` вызывает метод оркестратора `handle_entry(director=self, payload=...)`.
6. **Обогащение:** `Director` обогащает результат `UnifiedViewDTO` метаданными роутинга перед возвратом.

---

## 💻 Пример использования

В типичном сценарии `Director` используется внутри хендлера Aiogram для переключения пользователя на новую функциональную область (фичу).

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
    container: MyContainer, # Ваш DI-контейнер
    sender: ViewSender      # Сервис отправки сообщений
):
    # 1. Инициализируем Director для текущего запроса
    director = Director(
        container=container,
        state=state,
        user_id=callback.from_user.id,
        chat_id=callback.message.chat.id,
        trigger_id=callback.message.message_id # Для удаления старого сообщения
    )

    # 2. Переключаем сцену на "booking"
    # Director сам найдет BookingOrchestrator в контейнере,
    # установит нужный FSM-стейт и вызовет логику рендеринга.
    view = await director.set_scene(
        feature="booking",
        payload={"service_id": 42} # Данные для инициализации фичи
    )

    # 3. Отправляем результат пользователю
    if view:
        await sender.send(view)
```

---

## 🗺️ Карта модуля

| Компонент | Описание |
|:---|:---|
| **[📄 API Reference](../../../api/director.md)** | Технические детали класса `Director`. |
| **[📄 Protocols](../../../api/director.md#protocols)** | `OrchestratorProtocol`, `ContainerProtocol` и `SceneConfig`. |

---

**Последнее обновление:** 2025-03-09
