# ⚙️ Engine

[⬅️ Back](../../README.md) | [🏠 Docs Root](../../../README.md)

The `engine` module provides the core infrastructure for building and running an `aiogram` bot with `codex-bot`.

---

## 🧠 The Why

### Parametric Assembly
In a large bot, the main router and dispatcher can become cluttered with imports. The `engine` module solves this by using **Parametric Assembly** (via `RouterBuilder` and `BotBuilder`). This allows you to explicitly control the order of middleware and features without hardcoding them in a single file.

### Feature Discovery
The `FeatureDiscoveryService` automates the registration of features (routers, orchestrators, menu configs, and garbage states). This follows the **Django INSTALLED_APPS** pattern, making it easy to add or remove features by simply updating a list in your settings.

---

## 🔄 The Flow

1. **Discovery:** `FeatureDiscoveryService` scans the `installed_features` list and imports their `handlers.py` and `feature_setting.py`.
2. **Assembly:** `RouterBuilder` collects all `Router` objects from the discovered features and includes them in the main router.
3. **Configuration:** `BotBuilder` creates the `Bot` and `Dispatcher` instances, injecting the discovered features and middlewares in the specified order.
4. **Startup:** The bot starts polling, with all features and infrastructure (i18n, throttling, container) ready to handle requests.

---

## 💻 Bot Assembly Example

`BotBuilder` allows you to assemble the bot and dispatcher while explicitly controlling the order of middleware connections.

```python
import asyncio
from aiogram.fsm.storage.memory import MemoryStorage
from codex_bot.engine.factory.bot_builder import BotBuilder
from codex_bot.engine.middlewares.container import ContainerMiddleware
from codex_bot.engine.middlewares.throttling import ThrottlingMiddleware

async def main():
    # 1. Initialize the builder
    builder = BotBuilder(
        bot_token="YOUR_TOKEN",
        fsm_storage=MemoryStorage()
    )

    # 2. Add middlewares in the desired order
    # (e.g., container first, then throttling)
    builder.add_middleware(ContainerMiddleware(container=my_container))
    builder.add_middleware(ThrottlingMiddleware(redis=redis_client))

    # 3. Build the bot and dispatcher
    bot, dp = builder.build()

    # 4. Connect feature routers (via RouterBuilder)
    # dp.include_router(main_router)

    # 5. Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🗺️ Module Map

| Component | Description |
|:---|:---|
| **[📄 Router Builder](../../../api/router_builder.md)** | `build_main_router` and `collect_feature_routers`. |
| **[📄 Discovery](../../../api/discovery.md)** | `FeatureDiscoveryService` for auto-discovery and registration. |
| **[📄 Factory](../../../api/factory.md)** | `BotBuilder` for creating `Bot` and `Dispatcher`. |
| **[📄 Middlewares](../../../api/middlewares.md)** | `UserValidation`, `Throttling`, `Container`, and `I18n` middlewares. |
| **[📄 HTTP Client](../../../api/http.md)** | `BaseApiClient` with connection pooling. |
| **[📄 I18n Compiler](../../../api/i18n.md)** | `compile_locales` for Fluent (.ftl) files. |

---

**Last Updated:** 2025-03-09
