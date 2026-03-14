# API Reference

The technical reference for all modules and classes within the **codex-bot** library. Information here is automatically generated from the source code's docstrings.

---

## 🏛 Core API (Essential)
The foundational modules required for any project built with codex-bot.

| Component | Description |
| :--- | :--- |
| **[base](base.md)** | Abstract Orchestrator and core DTOs (UnifiedViewDTO). |
| **[director](director.md)** | Transition coordinator and Smart Resolver mechanism. |
| **[sender](sender.md)** | ViewSender service for SPA-like UI synchronization. |
| **[fsm](fsm.md)** | Isolated state management and BaseStateManager. |

---

## 🧩 Extensions (Optional)
Pluggable "batteries" to enhance your bot with additional features.

| Plugin | Description |
| :--- | :--- |
| **[redis](redis.md)** | Event-driven processing via Redis Streams. |
| **[animation](animation.md)** | Waiting animations for Telegram interactive UI. |
| **[helper](helper.md)** | Development utilities: ID Inspector and Context Helper. |
| **[url_signer](url_signer.md)** | HMAC security for Telegram Mini Apps. |

---

## ⚙️ Engine (Infrastructure)
The internal machinery responsible for bootstrapping and lifecycle.

| System | Description |
| :--- | :--- |
| **[factory](factory.md)** | BotBuilder — fluent interface for bot assembly. |
| **[discovery](discovery.md)** | Automated feature scanning and registration. |
| **[middlewares](middlewares.md)** | Standard processing layers (Throttling, Validation). |
| **[router_builder](router_builder.md)** | Automated assembly of the main application router. |
| **[http](http.md)** | BaseApiClient for REST interactions. |
| **[i18n](i18n.md)** | Localization engine and locales compilation. |

---

## 🏗 Architecture
For conceptual understanding, please refer to the **[Architecture Overview](../en_EN/architecture/README.md)**.
