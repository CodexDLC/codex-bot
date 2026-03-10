# 📂 Центр документации (Русский)

[🏠 Docs Root](../README.md)

Добро пожаловать в концептуальную документацию `codex-bot`. Этот раздел объясняет «Почему» и «Как» устроена архитектура фреймворка, помогая понять логику проектных решений.

---

## 🌟 Лучшие практики (Best Practices)

Рекомендуемые подходы к разработке на базе `codex-bot`:

- **[🚀 Обзор лучших практик](./guide/best_practices.md)** — Оглавление всех гайдов.
- **[⚙️ Конфигурация](./guide/infrastructure/configuration.md)** — Настройка через Pydantic v2.
- **[🏗️ DI-контейнер](./guide/infrastructure/di_container.md)** — Управление зависимостями.
- **[📂 Структура проекта](./guide/infrastructure/project_structure.md)** — Организация папок.
- **[🌍 Локализация и Сборка](./guide/infrastructure/i18n_factory.md)** — I18n и фабрика бота.
- **[📝 Логирование](./guide/infrastructure/logging.md)** — Профессиональная настройка Loguru.
- **[📱 Пример: Главное меню](./guide/examples/bot_menu.md)** — Реализация дашборда.

---

## 🗺️ Карта архитектуры

| Раздел | Описание |
|:---|:---|
| **[📦 Base](./architecture/base/README.md)** | Базовые DTO и абстрактный Оркестратор. |
| **[🧭 Director](./architecture/director/README.md)** | Координатор межфичевых переходов. |
| **[⚙️ Engine](./architecture/engine/README.md)** | Сборка роутеров, автообнаружение и фабрика бота. |
| **[🧠 FSM](./architecture/fsm/README.md)** | Управление состоянием и Garbage Collector. |
| **[🔄 Redis](./architecture/redis/README.md)** | Интеграция с Redis Stream и фоновая обработка. |
| **[📤 Sender](./architecture/sender/README.md)** | Доставка и синхронизация UI-сообщений. |
| **[🛠️ CLI](./architecture/cli/README.md)** | Команды генерации (scaffolding) новых фич. |
| **[✨ Animation](./architecture/animation/README.md)** | Анимации ожидания для Telegram UI. |
| **[🔗 URL Signer](./architecture/url_signer/README.md)** | HMAC-подписанные URL для Mini Apps. |
| **[🧰 Helper](./architecture/helper/README.md)** | Извлечение контекста и вспомогательные утилиты. |

---

## 📜 Философия проекта

`codex-bot` базируется на трех «китах»:

1. **Feature-based Isolation:** Каждая фича — это изолированный модуль со своей логикой, UI и ресурсами.
2. **Stateless Orchestrators:** Оркестраторы не хранят состояние пользователя в `self`. Весь контекст передается через `Director`.
3. **UI Persistence:** Фреймворк управляет двумя постоянными сообщениями (Menu и Content), чтобы минимизировать «мусор» в чате.

---

**Последнее обновление:** 2025-03-09
