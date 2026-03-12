# 🧩 Functional Feature Example

[⬅️ Back](../best_practices.md) | [🏠 Docs Root](../../../README.md)

> 🚧 **Work in Progress**
> This section is currently under development. It will contain a complete example of a pluggable feature with business logic, handlers, and configuration.

---

## 🏗️ What is a Feature?

In `codex-bot`, a **Feature** is a self-contained module that follows the **Django INSTALLED_APPS** pattern. It typically includes:

- `handlers.py` — Telegram handlers (routers).
- `feature_setting.py` — Feature-specific configuration.
- `orchestrators.py` — Business logic and service layer.
- `menu_config.py` — Menu structure and navigation.

---

## 🚀 Coming Soon

- Step-by-step guide to creating a new feature.
- Registering the feature in `installed_features`.
- Using dependency injection within a feature.
- Handling feature-specific states and garbage collection.

**Last Updated:** 2025-03-09
