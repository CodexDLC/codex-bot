# 📤 Sender

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

Модуль `sender` предоставляет stateless-сервис для отправки и синхронизации UI Telegram-бота в фреймворке `codex-bot`.

---

## 🧠 Почему так?

### Постоянство UI (UI Persistence)
В типичном боте каждое взаимодействие отправляет новое сообщение, создавая длинную и грязную историю чата. `ViewSender` решает это, управляя двумя **постоянными сообщениями** (Menu и Content). Вместо отправки новых сообщений он редактирует существующие, когда это возможно, сохраняя чат чистым и сфокусированным.

### Stateless-отправка
Поскольку `ViewSender` — это **Stateless Singleton**, он не хранит данные пользователя в `self`. Он использует `SenderManager` для получения текущих ID сообщений (координат) из постоянного хранилища (например, Redis) для каждого запроса. Это гарантирует консистентность UI даже при работе нескольких экземпляров бота.

---

## 🔄 Поток данных (The Flow)

1. **Вход:** `Director` вызывает оркестратор, который возвращает `UnifiedViewDTO`.
2. **Координация:** `ViewSender` получает `UnifiedViewDTO` и запрашивает текущие `menu_msg_id` и `content_msg_id` у `SenderManager`.
3. **Синхронизация:**
    - **Удаление:** Если присутствует `trigger_message_id` (например, `/start`), оно удаляется.
    - **Редактирование:** Если сообщения существуют, `ViewSender` редактирует их с новым контентом и клавиатурой.
    - **Создание:** Если их нет — отправляются новые сообщения.
4. **Сохранение:** `SenderManager` обновляет ID сообщений в хранилище для следующего запроса.

---

## 💻 Пример отправки сообщений

`ViewSender` управляет двумя постоянными сообщениями (Menu и Content), чтобы чат оставался чистым.

```python
from codex_bot.sender.view_sender import ViewSender
from codex_bot.base.view_dto import UnifiedViewDTO, ViewResultDTO

# 1. Создаем ViewSender (обычно через DI-контейнер)
sender = ViewSender(
    bot=bot,
    manager=sender_manager # Реализация SenderManagerProtocol
)

# 2. Подготавливаем данные для отправки
view = UnifiedViewDTO(
    content=ViewResultDTO(
        text="👋 Добро пожаловать в Codex Bot!",
        kb=main_keyboard
    ),
    menu=None, # Можно добавить постоянное меню
    chat_id=12345678,
    session_key=12345678
)

# 3. Отправляем (ViewSender сам решит: редактировать старое или отправить новое)
await sender.send(view)

# 4. Отправка с удалением триггерного сообщения (например, команды /start)
await sender.send(view, trigger_id=message.message_id)
```

---

## 🗺️ Карта модуля

| Компонент | Описание |
|:---|:---|
| **[📄 API Reference](../../../api/sender.md)** | Технические детали `ViewSender` и `SenderManager`. |
| **[📄 Sender Keys](../../../api/sender.md#senderkeys)** | Фабрика ключей для хранилища координат UI. |
| **[📄 Protocols](../../../api/sender.md#protocols)** | `SenderStateStorageProtocol` для хранилища координат UI. |

---

**Последнее обновление:** 2025-03-09
