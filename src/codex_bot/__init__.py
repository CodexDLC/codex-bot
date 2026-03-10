"""
codex_bot — Feature-based Aiogram framework library.

Reusable infrastructure for Telegram bots with stateless UI management,
Redis Stream integration, and advanced FSM capabilities.
"""

__version__ = "0.1.0"
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
