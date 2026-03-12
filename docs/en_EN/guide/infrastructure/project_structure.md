# 📂 Project Structure and Feature Discovery

[⬅️ Back to Best Practices](../best_practices.md)

The `codex-bot` framework uses the **Feature Discovery** pattern (similar to `INSTALLED_APPS` in Django). This allows you to break the bot into independent modules (features) and connect them by simply listing them in the config.

## 🛠 Feature Configuration Example (`settings.py`)

We recommend moving the lists of installed modules to a separate settings file.

```python
"""
Configuration for pluggable features and middleware.
"""

# 1. UI Features (contain Aiogram routers and orchestrators)
INSTALLED_FEATURES: list[str] = [
    "features.telegram.commands",
    "features.telegram.bot_menu",
    "features.telegram.notifications",
    "features.telegram.contacts_admin",
]

# 2. Listener Features (handle events from Redis Stream)
INSTALLED_REDIS_FEATURES: list[str] = [
    "features.redis.notifications",
    "features.redis.errors",
]

# 3. Middleware List (modules containing setup logic)
MIDDLEWARE_CLASSES: list[str] = [
    "middlewares.user_validation",
    "middlewares.throttling",
    "middlewares.security",
    "middlewares.container",
]
```

## 🏗️ Recommended Folder Structure

To ensure feature discovery works correctly, adhere to the following structure:

```text
src/
└── telegram_bot/
    ├── core/                # Core: settings, constants
    ├── features/            # Functional modules
    │   ├── telegram/        # UI features (handlers.py, orchestrator.py)
    │   └── redis/           # Background features (handlers.py)
    ├── middlewares/         # Custom middlewares
    ├── resources/           # Locales (.ftl), templates
    └── main.py              # Entry point
```

## 🔄 How it Works

At startup, the `FeatureDiscoveryService` iterates through these lists and automatically:
1. Imports routers from each feature's `handlers.py`.
2. Registers orchestrators in the DI container.
3. Connects Redis Stream handlers to the dispatcher.
4. Registers "garbage states" for the Garbage Collector.

## 💎 Benefits
1. **Modularity**: To disable a feature, simply remove it from the list.
2. **No Cycles**: Features do not import each other directly.
3. **Clean main.py**: You don't need to manually import dozens of routers and orchestrators.

---
**Last Updated:** 2025-03-09
