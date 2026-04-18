# Middlewares — The Request Pipeline

Middlewares in **codex-bot** form a processing chain through which every Telegram event passes. Their main tasks are to prepare the request context, perform security checks, and inject dependencies into handlers.

---

## ⚙️ Standard Stack

The framework provides a set of ready-to-use middlewares. in projects created via the CLI, these are connected within the `core/factory.py` file. You can flexibly manage the stack composition by enabling or disabling modules (Redis, i18n, DB) in your settings.

### 1. ContainerMiddleware (The Foundation)
Injects the DI container object into the request context (`data["container"]`). This is the base upon which all other components operate.

### 2. UserValidationMiddleware (Security)
Performs initial user verification against the database or cache. It allows for immediate blocking of banned users before they reach the business logic.

### 3. ThrottlingMiddleware (Anti-Spam)
Limits the frequency of requests (Rate Limiting). If a user clicks buttons too frequently, the middleware intercepts the request, protecting the bot's resources.

### 4. DirectorMiddleware (Context Injection)
Automatically creates a **Director** object for the current request. This allows you to accept `director: Director` directly as a handler argument.

### 5. I18nMiddleware (Localization)
An optional middleware that determines the user's language and configures the translation engine.

---

## ⚖️ Order and Configuration

The order of middleware registration in the `BotBuilder` is critical for stability:
1. **Infrastructure** first (Container).
2. **Security** next (Validation, Throttling).
3. **Business Context** last (Director, I18n).

If you use the standard project skeleton, the framework will automatically arrange them in the correct order within the `build_bot()` function.

---

## 🧭 Related Sections
- **[BotBuilder](./factory.md)** — The tool used to register middlewares.
- **[Director](../services/director/README.md)** — The primary object injected via these layers.
