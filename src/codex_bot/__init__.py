"""
Codex Bot Framework — Feature-oriented high-level Aiogram library.

Provides a robust infrastructure for scalable Telegram bot development,
emphasizing stateless UI orchestration, Redis Stream integration, and per-event
dependency injection. Designed for modular architectures using a 'convention
over configuration' approach.
"""

import importlib.metadata

try:
    __version__ = importlib.metadata.version("codex-bot")
except importlib.metadata.PackageNotFoundError:
    __version__ = "unknown"

__author__ = "Codex Team"
__license__ = "MIT"

from codex_bot.base.base_orchestrator import BaseBotOrchestrator, PayloadT
from codex_bot.director.director import Director
from codex_bot.engine.factory.bot_builder import BotBuilder
from codex_bot.sender.view_sender import ViewSender

__all__ = [
    "BaseBotOrchestrator",
    "PayloadT",
    "Director",
    "BotBuilder",
    "ViewSender",
    "__version__",
]
