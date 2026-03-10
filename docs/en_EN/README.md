# 📂 English Documentation Hub

[🏠 Docs Root](../README.md)

Welcome to the conceptual documentation for `codex-bot`. This section explains the "Why" and "How" behind the framework's architecture.

---

## 🗺️ Architecture Map

| Section | Description |
|:---|:---|
| **[📦 Base](./architecture/base/README.md)** | Core DTOs and the abstract Orchestrator. |
| **[🧭 Director](./architecture/director/README.md)** | Cross-feature transition coordinator. |
| **[⚙️ Engine](./architecture/engine/README.md)** | Router assembly, discovery, and bot factory. |
| **[🧠 FSM](./architecture/fsm/README.md)** | State management and Garbage Collector. |
| **[🔄 Redis](./architecture/redis/README.md)** | Redis Stream integration and background processing. |
| **[📤 Sender](./architecture/sender/README.md)** | UI message delivery and synchronization. |
| **[🛠️ CLI](./architecture/cli/README.md)** | Scaffolding commands for feature creation. |
| **[✨ Animation](./architecture/animation/README.md)** | Waiting animations for Telegram UI. |
| **[🔗 URL Signer](./architecture/url_signer/README.md)** | HMAC-signed URLs for Mini Apps. |
| **[🧰 Helper](./architecture/helper/README.md)** | Context extraction and utility helpers. |

---

## 📜 Core Philosophy

`codex-bot` is built on three main pillars:

1. **Feature-based Isolation:** Every feature is a self-contained module with its own logic, UI, and resources.
2. **Stateless Orchestrators:** Orchestrators do not store user state in `self`. All context is passed through the `Director`.
3. **UI Persistence:** The framework manages two persistent messages (Menu and Content) to minimize chat clutter.

---

**Last Updated:** 2025-02-07
