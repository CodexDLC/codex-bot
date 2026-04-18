# codex-bot

[![PyPI version](https://img.shields.io/pypi/v/codex-bot.svg)](https://pypi.org/project/codex-bot/)
[![Python versions](https://img.shields.io/pypi/pyversions/codex-bot.svg)](https://pypi.org/project/codex-bot/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**codex-bot** is a feature-based framework built on top of [Aiogram 3.x](https://github.com/aiogram/aiogram), providing professional-grade infrastructure for building complex Telegram bot ecosystems.

---

## Install

```bash
# Core framework only
pip install codex-bot

# Include Redis Stream integration
pip install "codex-bot[redis]"
```

## Quick Start

```python
import asyncio
from codex_bot.director import Director
from codex_bot.engine.discovery.service import FeatureDiscoveryService

async def main():
    # Auto-discovery of business features
    discovery = FeatureDiscoveryService(
        installed_features=["profile", "settings"]
    )
    discovery.discover_all()

    # Unified orchestration
    print("Codex-Bot ready for action!")

if __name__ == "__main__":
    asyncio.run(main())
```

## Modules

| Module | Extra | Description |
| :--- | :--- | :--- |
| `base` | - | Immutable DTOs and base orchestrator classes |
| `director` | - | Smart navigation and context management |
| `engine` | - | Convention-based feature discovery service |
| `stream` | `[redis]` | Redis Streams integration for async event handling |
| `fsm` | - | Namespaced FSM with automated garbage collection |

## Documentation

Full documentation with architecture diagrams, API reference, and guides:

**[https://codexdlc.github.io/codex-bot/](https://codexdlc.github.io/codex-bot/)**

## Part of the Codex ecosystem

| Library | Description |
| :--- | :--- |
| [codex-core](https://github.com/codexdlc/codex-core) | Shared DTOs, logging, and security |
| [codex-platform](https://github.com/codexdlc/codex-platform) | Infrastructure: Redis, Workers, Notifications |
| [codex-ai](https://github.com/codexdlc/codex-ai) | Agnostic LLM abstraction layer |
| [codex-services](https://github.com/codexdlc/codex-services) | Domain engines: Booking, Payments, CRM |

Each library is fully standalone — install only what your project needs. Together they form the backbone of **codex-bot** (aiogram) and **codex-django** (Django integration layer).

---

## License
This project is licensed under the **Apache License 2.0**. Developed by **Codex Team**.
