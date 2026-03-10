# 🏗️ DI Container (Dependency Injection)

[⬅️ Back to Best Practices](../best_practices.md)

Centralizing all dependencies in a single object (`BotContainer`) is the key to clean code. The container manages the lifecycle of services, API clients, and orchestrators.

## 🛠 Container Implementation Example

```python
import socket
from typing import Any
from aiogram import Bot
from codex_bot.engine.discovery.service import FeatureDiscoveryService
from codex_bot.redis.dispatcher import BotRedisDispatcher
from codex_bot.redis.stream_processor import RedisStreamProcessor
from codex_bot.sender.view_sender import ViewSender

class BotContainer:
    """
    DI Container for the Telegram Bot.
    """
    def __init__(self, settings: BotSettings, redis_client: Redis):
        self.settings = settings
        self.redis_client = redis_client
        self.bot: Bot | None = None
        self.view_sender: ViewSender | None = None

        # --- API Clients ---
        self.admin_api = AdminApiProvider(base_url=self.settings.api_url)

        # --- Redis Infrastructure ---
        self.redis_dispatcher = BotRedisDispatcher()
        self.stream_processor = RedisStreamProcessor(
            storage=RedisStreamAdapter(redis_client),
            stream_name="bot_events",
            consumer_group_name="bot_group",
            consumer_name=f"bot_{socket.gethostname()}"
        )

        # --- Feature Discovery ---
        self.discovery_service = FeatureDiscoveryService(
            module_prefix="src.telegram_bot",
            installed_features=INSTALLED_FEATURES,
            redis_dispatcher=self.redis_dispatcher,
        )
        self.discovery_service.discover_all()

        # --- Orchestrator Initialization ---
        self.features = self.discovery_service.create_feature_orchestrators(self)

    def set_bot(self, bot: Bot) -> None:
        """Links the Bot object to the container and configures dispatchers."""
        self.bot = bot
        self.view_sender = ViewSender(bot=self.bot)
        self.redis_dispatcher.setup(container=self)
        self.stream_processor.set_message_callback(self.redis_dispatcher.process_message)

    async def shutdown(self):
        """Graceful shutdown of all resources."""
        await self.admin_api.close()
        await self.stream_processor.stop_listening()
        await self.redis_client.close()
```

## 💎 Benefits
1. **Single Source of Truth**: All services (API, Redis, Orchestrators) are accessible via `container`.
2. **Lifecycle Management**: The `shutdown` method ensures all connections are closed correctly.
3. **Automation**: `FeatureDiscoveryService` finds and creates orchestrators automatically, eliminating manual registration.
4. **Adaptability**: Using adapters (like `RedisStreamAdapter`) allows easy integration of external libraries with framework protocols.

---
**Last Updated:** 2025-03-09
