# Codex Bot Framework

[![PyPI version](https://img.shields.io/pypi/v/codex-bot.svg)](https://pypi.org/project/codex-bot/)
[![Python versions](https://img.shields.io/pypi/pyversions/codex-bot.svg)](https://pypi.org/project/codex-bot/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Codex Bot** is a professional, feature-based framework built on top of [Aiogram 3.x](https://github.com/aiogram/aiogram). It provides a reusable, production-ready infrastructure for building complex, scalable Telegram bots with a focus on stateless UI management and high-load Redis integration.

---

## 🚀 Key Features

- **Feature-based Architecture**: Organize your bot into independent, reusable features.
- **Stateless Orchestrators**: Manage UI logic without storing state in memory, making your bot horizontally scalable.
- **Redis Stream Integration**: Native support for high-load event processing with Consumer Groups.
- **Advanced FSM**: Automatic UI cleanup with `GarbageStateRegistry` and structured state management.
- **Unified View System**: Consistent message rendering across different platforms using DTOs.
- **Fluent-based I18n**: Powerful localization engine with project-level isolation and automatic compilation.
- **CLI Scaffolding**: Rapidly generate new features with pre-defined templates.

---

## 📦 Installation

Install the core library:
```bash
pip install codex-bot
```

Install with optional dependencies:
```bash
pip install "codex-bot[redis,i18n,http]"
```

---

## 🛠 Quick Start

```python
from codex_bot import BotBuilder, BaseBotOrchestrator, Director
from codex_bot.base.view_dto import ViewResultDTO

# 1. Define your feature orchestrator
class MyFeatureOrchestrator(BaseBotOrchestrator[None]):
    async def render_content(self, payload: None, director: Director) -> ViewResultDTO:
        return ViewResultDTO(text="Hello from Codex Bot!")

# 2. Build and run your bot
builder = BotBuilder(token="YOUR_TELEGRAM_TOKEN")
builder.register_orchestrator("main", MyFeatureOrchestrator())
builder.run_polling()
```

---

## 📚 Documentation

- [English Documentation](https://codexdlc.github.io/codex-bot/en_EN/)
- [Русская документация](https://codexdlc.github.io/codex-bot/ru_RU/)
- [**Changelog**](CHANGELOG.md) — see what's new in the latest versions.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

### 🇷🇺 Краткое описание (RU)
**Codex Bot** — это профессиональный фреймворк для создания Telegram-ботов на базе Aiogram 3.x. Он предоставляет готовую инфраструктуру для разработки сложных и масштабируемых систем, используя архитектуру на основе "фич", stateless-оркестраторы и глубокую интеграцию с Redis Streams.
