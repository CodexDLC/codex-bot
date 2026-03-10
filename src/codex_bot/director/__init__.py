"""
codex_bot.director — Cross-feature transition coordinator.
"""

from codex_bot.director.director import Director
from codex_bot.director.protocols import ContainerProtocol, OrchestratorProtocol, SceneConfig

__all__ = [
    "Director",
    "OrchestratorProtocol",
    "ContainerProtocol",
    "SceneConfig",
]
