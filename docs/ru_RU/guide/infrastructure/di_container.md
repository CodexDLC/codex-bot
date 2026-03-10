# 🏗️ DI-контейнер (Dependency Injection)

[⬅️ Назад к списку гайдов](best_practices.md)

Централизация всех зависимостей в одном объекте (`BotContainer`) — это ключ к чистому коду. Контейнер управляет жизненным циклом сервисов, API-клиентов и оркестраторов.

## 🛠 Пример реализации контейнера

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
    DI Контейнер для Telegram-бота.
    """
    def __init__(self, settings: BotSettings, redis_client: Redis):
        self.settings = settings
        self.redis_client = redis_client
        self.bot: Bot | None = None
        self.view_sender: ViewSender | None = None

        # --- Инфраструктура Redis ---
        self.redis_dispatcher = BotRedisDispatcher()
        self.stream_processor = RedisStreamProcessor(
            storage=RedisStreamAdapter(redis_client),
            stream_name="bot_events",
            consumer_group_name="bot_group",
            consumer_name=f"bot_{socket.gethostname()}"
        )

        # --- Автообнаружение фич ---
        self.discovery_service = FeatureDiscoveryService(
            module_prefix="src.telegram_bot",
            installed_features=INSTALLED_FEATURES,
            redis_dispatcher=self.redis_dispatcher,
        )
        self.discovery_service.discover_all()

        # --- Инициализация оркестраторов ---
        self.features = self.discovery_service.create_feature_orchestrators(self)

    def set_bot(self, bot: Bot) -> None:
        """Связывает объект Bot с контейнером и настраивает диспетчеры."""
        self.bot = bot
        self.view_sender = ViewSender(bot=self.bot)
        self.redis_dispatcher.setup(container=self)
        self.stream_processor.set_message_callback(self.redis_dispatcher.process_message)

    async def shutdown(self):
        """Корректное закрытие всех ресурсов."""
        await self.admin_api.close()
        await self.stream_processor.stop_listening()
        await self.redis_client.close()
```

## 💎 Преимущества подхода
1. **Единая точка правды**: Все сервисы (API, Redis, Оркестраторы) доступны через `container`.
2. **Управление жизненным циклом**: Метод `shutdown` гарантирует, что все соединения будут закрыты корректно.
3. **Автоматизация**: `FeatureDiscoveryService` сам находит и создает оркестраторы, избавляя от ручной регистрации.
4. **Адаптивность**: Использование адаптеров (как `RedisStreamAdapter`) позволяет легко интегрировать внешние библиотеки под протоколы фреймворка.

---
**Последнее обновление:** 2025-03-09
