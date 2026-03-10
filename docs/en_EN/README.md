# 📂 Documentation Center (English)

[🏠 Docs Root](../README.md)

Welcome to the conceptual documentation of `codex-bot`. This section explains the "Why" and "How" behind the framework's architecture, helping you understand the logic of design decisions.

---

## 🌟 Best Practices

Recommended approaches for development based on `codex-bot`:

- **[🚀 Best Practices Overview](./guide/best_practices.md)** — Index of all guides.
- **[⚙️ Configuration](./guide/infrastructure/configuration.md)** — Setup via Pydantic v2.
- **[🏗️ DI Container](./guide/infrastructure/di_container.md)** — Dependency management.
- **[📂 Project Structure](./guide/infrastructure/project_structure.md)** — Folder organization.
- **[🌍 Localization & Factory](./guide/infrastructure/i18n_factory.md)** — I18n and bot factory.
- **[📝 Logging](./guide/infrastructure/logging.md)** — Professional Loguru setup.
- **[📱 Example: Main Menu](./guide/examples/bot_menu.md)** — Dashboard implementation.

---

## 🗺️ Architecture Map

| Section | Description |
|:---|:---|
| **[📦 Base](./architecture/base/README.md)** | Core DTOs and abstract Orchestrator. |
| **[🧭 Director](./architecture/director/README.md)** | Cross-feature transition coordinator. |
| **[⚙️ Engine](./architecture/engine/README.md)** | Router assembly, discovery, and bot factory. |
| **[🧠 FSM](./architecture/fsm/README.md)** | State management and Garbage Collector. |
| **[🔄 Redis](./architecture/redis/README.md)** | Redis Stream integration and background processing. |
| **[📤 Sender](./architecture/sender/README.md)** | UI message delivery and synchronization. |
| **[🛠️ CLI](./architecture/cli/README.md)** | Scaffolding commands for new features. |
| **[✨ Animation](./architecture/animation/README.md)** | Waiting animations for Telegram UI. |
| **[🔗 URL Signer](./architecture/url_signer/README.md)** | HMAC-signed URLs for Mini Apps. |
| **[🧰 Helper](./architecture/helper/README.md)** | Context extraction and utility tools. |

---

## 📜 Project Philosophy

`codex-bot` is built on three pillars:

1. **Feature-based Isolation:** Each feature is an isolated module with its own logic, UI, and resources.
2. **Stateless Orchestrators:** Orchestrators do not store user state in `self`. All context is passed via the `Director`.
3. **UI Persistence:** The framework manages two persistent messages (Menu and Content) to minimize chat clutter.

---

**Last Updated:** 2025-03-09
