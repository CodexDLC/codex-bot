# Codex Bot Framework 🚀

Welcome to the **codex-bot** documentation — a modern Aiogram-based framework for Telegram bots, focusing on modularity, clean architecture, and rapid development.

---

## 🏗 Key Features

- **Feature-based structure**: Each bot function is an independent module with its own logic, UI, and handlers.
- **Stateless Orchestrators**: All business logic is separated from the user state, making scaling effortless.
- **Smart UI Synchronization**: Automatically update existing messages instead of spamming with new ones.
- **Event-Driven**: Built-in Redis Streams support for background task processing.

---

## 🗺 System Map

### 🚀 Quick Start
- **[Getting Started](./guide/getting_started.md)**: From installation to your first bot in 5 minutes.
- **[CLI Engine](./architecture/cli/README.md)**: How to use the project and feature generator.

### 🏛 Architecture & Engine
- **[Architecture Overview](./architecture/README.md)**: How everything works under the hood.
- **[Feature Discovery](./architecture/engine/discovery.md)**: The magic of automated module connection.
- **[Bot Factory](./architecture/engine/factory.md)**: Flexible assembly and middleware configuration.

### 🛠 Core Services
- **[Director](./architecture/services/director/README.md)**: Orchestrating transitions between scenes.
- **[ViewSender](./architecture/services/view_sender/README.md)**: UI delivery and message synchronization.
- **[FSM & States](./architecture/services/fsm/README.md)**: Isolated user data storage.
- **[Redis Streams](./architecture/services/redis/README.md)**: Handling asynchronous events.
- **[Helpers](./architecture/services/helper/README.md)**: Useful utilities and ID inspector.

---

## 📚 API Reference
For detailed information on specific classes and methods, check our **[Technical Reference](../api/README.md)**. You can also view our development plans in the **[Roadmap](./roadmap.md)** and active **[Backlog](./tasks/backlog.md)**.
