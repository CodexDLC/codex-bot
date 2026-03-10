"""
codex_bot.engine.router_builder — Parametric assembly of the main router.
"""

from codex_bot.engine.router_builder.router_builder import build_main_router, collect_feature_routers

__all__ = [
    "collect_feature_routers",
    "build_main_router",
]
