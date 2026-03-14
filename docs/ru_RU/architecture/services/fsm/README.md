# Управление состоянием (FSM)

В **codex-bot** работа с FSM (Finite State Machine) строится на принципе строгой изоляции данных. Мы используем **Namespacing (Пространства имен)**, чтобы фичи не конфликтовали друг с другом.

---

## 🏛 BaseStateManager

`BaseStateManager` — это базовый класс для управления данными конкретной фичи. Он изолирует данные под ключом `draft:<feature_key>` внутри общего хранилища пользователя.

### Зачем это нужно?
1. **Безопасность**: Фича "Профиль" никогда не перезапишет данные фичи "Бронирование".
2. **Чистота**: Вы всегда знаете, какая часть данных к какой фиче относится.
3. **Производительность**: При очистке данных фичи удаляется только её ключ (`clear()`), не затрагивая остальное состояние.

---

## ✍️ Как использовать (Пример)

Обычно для каждой фичи создается свой менеджер состояний, наследуемый от `BaseStateManager`.

### 1. Создание кастомного менеджера:
```python
from codex_bot.fsm.state_manager import BaseStateManager

class BookingStateManager(BaseStateManager):
    def __init__(self, state):
        # Передаем уникальный ключ фичи
        super().__init__(state, feature_key="booking")

    async def save_hotel(self, hotel_id: int):
        await self.update(hotel_id=hotel_id)

    async def get_hotel(self) -> int | None:
        return await self.get_value("hotel_id")
```

### 2. Использование в оркестраторе:
```python
async def render_content(self, payload, director: Director):
    # Создаем менеджер, передавая ему director.state
    fsm = BookingStateManager(director.state)

    # Читаем или обновляем данные
    hotel_id = await fsm.get_hotel()
    ...
```

---

## 🔄 FSM в Telegram vs Redis/Webhooks

Это ключевое различие в доступе к состояниям:

### 1. Telegram-фичи (User-Driven)
Когда пользователь взаимодействует с ботом в чате, у нас есть живой `FSMContext`. Мы работаем через `BaseStateManager` и `director.state`.

### 2. Внешние события (Redis Streams / Webhooks)
События извне приходят асинхронно. В этот момент у нас **нет активного `FSMContext`**, так как сессия пользователя не инициирована из чата.

- **Логика**: Если внешнему сервису нужно изменить состояние пользователя (например, переключить его на экран «Оплата прошла»), он должен обращаться к хранилищу напрямую через `container.storage`, используя `user_id` из данных события.
- **Сценарий**: "Ловим событие -> Находим юзера -> Обновляем его стейт в Redis -> Отправляем пуш через ViewSender".

---

## 🚮 Garbage Collector (Очистка UI)

`GarbageStateRegistry` использует FSM для отслеживания «мусорных» сообщений. Бот автоматически удаляет старые клавиатуры и временные уведомления при смене состояния пользователя, поддерживая чистоту в чате.

---

## 🧭 Связанные компоненты
- **[Director](../director/README.md)** — мост к `FSMContext` в Telegram-фичах.
- **[ViewSender](../view_sender/README.md)** — использует данные FSM для поиска ID сообщений.
