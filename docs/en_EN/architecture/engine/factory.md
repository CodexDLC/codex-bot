# BotBuilder (Factory) — Project Assembly

**BotBuilder** is a Builder pattern for creating `Bot` and `Dispatcher` objects with automated infrastructure configuration.

---

## 🏗 Rock-solid Core
The builder ensures that system middlewares are connected in a strict, unchangeable order:

1.  **Database** (optional) — opens transactions.
2.  **Container** — dependency injection.
3.  **Throttling** (optional) — anti-spam protection.
4.  **Director** — navigation initialization.
5.  **User Validation** — RBAC and user context.

---

## ⚡️ Auto-integration
You no longer need to manually link the Bot and Container. The `build()` method automatically calls `container.set_bot(bot)`, initializing all internal services (like ViewSender).

```python
builder = BotBuilder(bot_token=settings.bot_token)
builder.setup_core(container=container) # Integration happens here
bot, dp = builder.build()
```

---

## 🧩 Custom Middlewares
You can add your own layers via the `CUSTOM_MIDDLEWARES` list in `settings.py`. They will be automatically registered **after** the core framework ones, with full access to all services and the Director.
