# 🤖 codex-bot Documentation

Welcome to the official documentation for `codex-bot` — a professional, feature-based framework library for building scalable Telegram bots with Aiogram 3.x.

---

## 🌎 Choose Your Language

Select your preferred language to explore the guides, architecture, and best practices.

| Language | Description |
|:---|:---|
| **[🇬🇧 English Guide](./en_EN/README.md)** | **Primary Documentation.** Includes architecture, CLI guides, and core concepts. |
| **[🇷🇺 Русское руководство](./ru_RU/README.md)** | **Концептуальный перевод.** Описание архитектуры и ментальная модель разработчика. |

---

## 🏗️ Core Architecture at a Glance

Codex Bot is built on three pillars:

- **The Director**: Request-level context and cross-feature transitions.
- **Orchestrators**: Stateless logic for rendering UI from data.
- **ViewSender**: Atomic synchronization of persistent Menu and Content messages.

---

## 🛠️ Quick Installation & Setup

### 1. Install the Core
```bash
pip install codex-bot
```

### 2. Generate Your Project (Interactive Wizard)
```bash
codex-bot startproject my_bot
```
The CLI will automatically add necessary dependencies (`redis`, `db`, `i18n`, `arq`) to your project's `pyproject.toml` based on your stack preferences.

---

## 📄 Technical Reference

| Section | Description |
|:---|:---|
| **[📚 API Reference](./api/README.md)** | Full technical API documentation automatically generated from source code docstrings. |
| **[🗺️ Roadmap](./en_EN/roadmap.md)** | Planned features and infrastructure testing coverage. |
| **[🧭 Standards](./DOCUMENTATION_STANDARD.md)** | Documentation standards and how we structure our guides. |

---

**Last Updated:** 2025-02-07 | [GitHub Repository](https://github.com/codexdlc/codex-bot)
