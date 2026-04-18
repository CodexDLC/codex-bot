"""
codex_bot.engine — Infrastructure Core (Framework "Under-the-Hood" Logic).

This package contains the foundational components required for bot orchestration,
scaffolding, and lifecycle management. These modules are typically managed by
the framework itself and are not intended for frequent modification by feature
developers.

Sub-modules:
    engine.middlewares    — System-level middlewares (Throttling, Security, DI, etc.).
    engine.discovery      — FeatureDiscoveryService for automated module registration.
    engine.factory        — BotBuilder and resource compilation utilities.
    engine.router_builder — Logic for collecting and assembling feature routers.
    engine.http           — Base client abstractions for external API integration.
"""
