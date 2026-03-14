# codex-bot Framework 🚀

[![PyPI version](https://img.shields.io/pypi/v/codex-bot.svg)](https://pypi.org/project/codex-bot/)
[![Python versions](https://img.shields.io/pypi/pyversions/codex-bot.svg)](https://pypi.org/project/codex-bot/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**codex-bot** is a professional, industrial-grade framework built on top of [Aiogram 3.x](https://github.com/aiogram/aiogram). It provides a robust, **feature-based** architecture for building complex Telegram ecosystems, from standalone bots to smart clients driven by external backends.

---

## 💻 How it looks in code

Clean, state-independent orchestrators with automated dependency injection and **Smart Navigation**:

```python
# features/telegram/profile/logic/orchestrator.py
from codex_bot.base import BaseBotOrchestrator, ViewResultDTO, UnifiedViewDTO
from codex_bot.director import Director

class ProfileOrchestrator(BaseBotOrchestrator[dict]):
    async def render_content(self, payload: dict, director: Director) -> ViewResultDTO | UnifiedViewDTO:
        # 1. Fetch data via API/DB (Returns Envelope: meta + payload)
        raw_response = await director.container.api.get_user_profile(director.user_id)

        # 2. THE KILLER FEATURE: Smart Resolver
        # If your backend returns "X-Bot-Next-Scene: banned",
        # the Director automatically switches the user to the "banned" scene.
        data = await director.resolve(raw_response)

        if isinstance(data, UnifiedViewDTO):
            return data  # Seamless redirect managed by the backend!

        # 3. Pure business logic with clean UI separation
        return self.ui.render_profile_screen(data)
```

---

## 💎 Key Philosophy & Features

### 🏛 Stateless Architecture & Smart Resolver
Orchestrators and services do not store user state in memory. All request context is encapsulated within the `Director` object. With the **Smart Resolver** pattern, the Director can automatically handle navigation instructions received from any data source, making your bot horizontally scalable and backend-driven.

### 🧩 Feature-based Organization
Independent business modules (features) with isolated handlers, logic, and FSM namespaces.
- **Convention over Configuration**: `FeatureDiscoveryService` automatically finds and registers features, routers, and orchestrators.
- **Namespaced FSM**: `BaseStateManager` isolates data under `draft:<feature_key>`, preventing data collisions.

### 🧹 Smart UI & Garbage Collection
- **ViewSender Service**: Manages persistent **Menu** and **Content** messages. It synchronizes UI by editing messages, ensuring a "Single Page Application" feel.
- **Garbage Collector**: Automatically deletes old UI elements (keyboards/messages) during transitions or flow completion.

### 🌍 Professional I18n Engine
A powerful localization system built for multi-bot environments with path-based isolation and automatic Fluent (.ftl) compilation.

---

## 🚀 Quick Start (CLI)

### 1. Initialize Project
```bash
# Works for new AND existing projects (Django, FastAPI, etc.)
codex-bot startproject my_bot
```

### 2. Add Feature & Run
```bash
codex-bot create-feature  # Interactive wizard
python manage.py run
```

---

## 🔄 Redis Stream Integration
Handle background events with familiar decorator-based syntax:

```python
@redis_router.message("order.confirmed")
async def handle_order(payload: dict, container: BaseBotContainer):
    await container.view_sender.send_content(
        chat_id=payload["user_id"],
        text="✅ Your order is confirmed!"
    )
```

---

## 📚 Documentation Center

*   🌐 **[English Documentation](https://codexdlc.github.io/codex-bot/en_EN/)** (including **[Roadmap](./docs/en_EN/roadmap.md)**)
*   🇷🇺 **[Русская документация](https://codexdlc.github.io/codex-bot/ru_RU/)** (раздел **[Roadmap](./docs/ru_RU/roadmap.md)**)
*   📜 **[Changelog](./CHANGELOG.md)** — See what's new in the latest version.

---

## 📄 License
This project is licensed under the **Apache License 2.0**. Developed by **Codex Team**.
