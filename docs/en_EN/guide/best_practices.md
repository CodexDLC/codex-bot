# 🌟 Best Practices

[⬅️ Back](../README.md) | [🏠 Docs Root](../../README.md)

This section contains time-tested approaches for developing bots based on `codex-bot`. These patterns will help you create scalable, secure, and easily maintainable systems.

---

## 🏗️ 1. Project Setup (Infrastructure)
How to prepare the foundation for a scalable bot:

- **[📂 Project Structure](./infrastructure/project_structure.md)** — Folder organization and feature discovery.
- **[⚙️ Configuration](./infrastructure/configuration.md)** — Managing settings via Pydantic v2.
- **[🏗️ DI Container](./infrastructure/di_container.md)** — Centralizing dependencies and services.
- **[🌍 Localization & Factory](./infrastructure/i18n_factory.md)** — Working with Fluent locales and BotBuilder.
- **[📝 Logging](./infrastructure/logging.md)** — Professional Loguru setup.

---

## 🚀 2. Feature Implementation Examples
Ready-to-use templates for different types of functionality:

- **[📱 Main Menu (Dashboard)](./examples/bot_menu.md)** — Example of a "top-level" system feature that manages navigation.
- **[🧩 Functional Feature](./examples/feature.md)** — (In Progress) Example of a regular pluggable feature with business logic.

---

## 💎 Why is this important?
Following these practices ensures that your bot will be **Stateless**, **Scalable**, and **Easy to test**.

**Last Updated:** 2025-03-09
