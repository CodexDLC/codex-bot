# Container — Dependency Injection

`BaseBotContainer` is the central registry for all services, settings, and features of your project. It implements the Dependency Injection pattern, providing access to required objects from any part of the code through the Director object.

---

## 🏛 The Role of the Container

The container is created once at bot startup and performs the following tasks:
1. **Singleton Storage**: Database clients, API clients, settings, and the bot object itself live here.
2. **ViewSender Management**: The container initializes the UI delivery service as soon as the `Bot` object is passed into it.
3. **Feature Registry**: All orchestrators found via the `DiscoveryService` are registered here. The Director consults the container to find the required "scene."
4. **Centralized RBAC**: The `is_admin()` method provides a single place to define access control logic (e.g., via an `owner_ids` list).

---

## 🔄 Lifecycle

1. **Initialization**: The container is created with a settings object and (optionally) a Redis client.
2. **Feature Registration**: Discovery populates the `container.features` dictionary.
3. **Bot Binding**: `container.set_bot(bot)` is called, which activates the `ViewSender`.
4. **Operation**: The container object is passed into each request via Middleware.
5. **Shutdown**: When the bot is turned off, `container.shutdown()` is called, automatically closing connections in all registered features.

---

## ✍️ Customization

Typically, a project creates its own `BotContainer` class inheriting from the base one. This allows you to add services specific to your bot:

```python
class MyBotContainer(BaseBotContainer):
    def __init__(self, settings, redis):
        super().__init__(settings, redis)
        # Adding custom services
        self.db = MyDatabaseClient(settings.db_url)
        self.stats = AnalyticsService()
```

---

## 🧭 Related Sections
- **[Director](../services/director/README.md)** — Provides access to the container within orchestrators.
- **[Discovery](./discovery.md)** — Populates the container with orchestrators.
- **[API: BaseBotContainer](../../../api/factory.md)** — Technical method descriptions.
