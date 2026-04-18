# Discovery — Automation and Conventions

The `FeatureDiscoveryService` is a mechanism that frees the developer from manually registering every new feature. It implements the "Convention over Configuration" principle: you simply create a directory following the standard, and the engine handles the rest.

---

## 📂 Path Convention and Module Prefix

Discovery operates using a **module prefix** (typically `{project_name}.features`). This allows the service to correctly import files from your `src` layout.

For Discovery to find your feature, it must be located at these paths:

- **Telegram Features**: `...features/telegram/{feature_name}/`
- **Redis Features**: `...features/redis/{feature_name}/`

Inside each such directory, a `feature_setting.py` file is **required**.

---

## 📜 The `feature_setting.py` Contract

This file serves as the feature's "passport." Discovery scans it for:

1. **`create_orchestrator(container)`**: A factory function for instantiating the orchestrator.
2. **`MENU_CONFIG`**: Settings for the Dashboard menu button.
3. **`GARBAGE_STATES` / `GARBAGE_COLLECT`**: Configuration for automated message cleanup.

---

## ⚙️ What Discovery Automates

### 1. Router Collection (RouterBuilder)
Discovery is tightly integrated with the `RouterBuilder` — a component that assembles all scattered feature routers into a single **Main Application Router**.
- **Fail Fast**: If there is an error in the handler code, the bot will fail with a critical error immediately at startup. This prevents running a "broken" bot.
- **Exporting**: The feature's router must be accessible within the `handlers/__init__.py` file.

### 2. Redis Handler Collection
For Redis features, the service looks for a `redis_router` within the `handlers` package and registers it within the `BotRedisDispatcher`.

### 3. Container Registration
All orchestrators created via factories are registered in `container.features`. This enables the Director to find them by key during transitions.

---

## 🧭 Related Sections
- **[API: Discovery Service](../../../api/discovery.md)** — Technical description of methods.
- **[Director](../services/director/README.md)** — Uses orchestrators assembled via Discovery.
