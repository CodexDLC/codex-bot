# Engine — The Core Infrastructure

The `Engine` is a collection of systems responsible for the bot's lifecycle, automated component assembly, and integration with external services. This is where the "magic" of **codex-bot** happens, allowing you to write significantly less boilerplate code.

---

## 💎 Engine Philosophy

The engine is built on the **Convention over Configuration** principle. This means that by following a standardized directory structure, the engine will automatically discover your features, connect routers, and configure translations without a single line of manual registration.

---

## 🏗 Key Subsystems

| Subsystem | Purpose | Description |
| :--- | :--- | :--- |
| **[Discovery](./discovery.md)** | Auto-feature Search | Scans directories and registers orchestrators and routers. |
| **[BotBuilder](./factory.md)** | Bot Assembler | A fluent interface for configuring the Bot, Dispatcher, and Middleware. |
| **[Container](./container.md)** | DI Container | A centralized registry for all project services and clients. |
| **[Middlewares](./middlewares.md)** | Middlewares | Standard stack: Throttling, User Validation, and Director Injection. |
| **[I18n](./i18n.md)** | Localization | Smart translation management and path-based locale isolation. |
| **[HTTP/DB](./http_db.md)** | Clients | Base abstractions for interacting with APIs and databases. |

---

## 🚀 Startup Flow

When you start the bot, the Engine performs the following steps:
1. **Container Initialization**: Settings and clients (DB, Redis) are loaded.
2. **Discovery**: Features are scanned, and orchestrators are instantiated.
3. **BotBuilder**: The Dispatcher object is assembled, and all system middlewares are connected.
4. **I18n**: Locales are compiled, and the translation middleware is attached.
5. **Startup**: The bot begins listening to Telegram and (if configured) Redis Streams. The framework activates only the subsystems you explicitly enabled.
6. **Webhooks**: A web server is started to handle incoming webhooks (currently in development).

---

## 🧭 Related Components
- **[Director](../services/director/README.md)** — uses data prepared by the engine.
- **[ViewSender](../services/view_sender/README.md)** — initialized via the BotBuilder.
