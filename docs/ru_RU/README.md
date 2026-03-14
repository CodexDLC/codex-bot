# Codex Bot Framework 🚀

Добро пожаловать в документацию **codex-bot** — современного фреймворка для разработки Telegram-ботов на базе aiogram с акцентом на модульность, чистоту архитектуры и высокую скорость разработки.

---

## 🏗 Ключевые особенности

- **Feature-based структура**: Каждая функция бота — это независимый модуль со своей логикой, UI и хендлерами.
- **Stateless Orchestrators**: Вся бизнес-логика отделена от состояния пользователя, что упрощает масштабирование.
- **Smart UI Synchronization**: Автоматическое обновление сообщений вместо спама новыми уведомлениями.
- **Event-Driven**: Встроенная поддержка Redis Streams для обработки фоновых задач.

---

## 🗺 Карта системы

### 🚀 Быстрый старт
- **[Начало работы](./guide/getting_started.md)**: От установки до первого эхо-бота за 5 минут.
- **[Движок CLI](./architecture/cli/README.md)**: Как использовать генератор проектов и фич.

### 🏛 Архитектура и Движок
- **[Обзор архитектуры](./architecture/README.md)**: Как всё устроено под капотом.
- **[Feature Discovery](./architecture/engine/discovery.md)**: Магия автоматического подключения модулей.
- **[Bot Factory](./architecture/engine/factory.md)**: Гибкая сборка и настройка мидлварей.

### 🛠 Ключевые сервисы
- **[Director](./architecture/services/director/README.md)**: Координация переходов между сценами.
- **[ViewSender](./architecture/services/view_sender/README.md)**: Доставка и синхронизация интерфейса.
- **[FSM & States](./architecture/services/fsm/README.md)**: Изолированное хранение данных пользователя.
- **[Redis Streams](./architecture/services/redis/README.md)**: Обработка асинхронных событий.
- **[Helpers](./architecture/services/helper/README.md)**: Полезные утилиты и ID-инспектор.

---

## 📚 API Reference
Если вам нужны подробности о конкретных классах и методах, загляните в наш **[Технический справочник](../api/README.md)**. Вы также можете ознакомиться с планами развития в **[Roadmap](./roadmap.md)** и текущим **[Бэклогом](./tasks/backlog.md)**.
