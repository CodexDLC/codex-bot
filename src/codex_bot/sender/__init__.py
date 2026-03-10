"""
codex_bot.sender — ViewSender, SenderManager, and UI coordinate storage protocols.
"""

from codex_bot.sender.protocols import SenderStateStorageProtocol
from codex_bot.sender.sender_keys import SenderKeys
from codex_bot.sender.sender_manager import SenderManager
from codex_bot.sender.view_sender import ViewSender

__all__ = [
    "SenderStateStorageProtocol",
    "SenderKeys",
    "SenderManager",
    "ViewSender",
]
