"""
codex_bot.cli — Project management commands.

Usage:
    codex-bot create-feature my_feature
    codex-bot create-feature my_feature --type redis
"""

from codex_bot.cli.commands import main

__all__ = ["main"]
