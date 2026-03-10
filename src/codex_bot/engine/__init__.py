"""
codex_bot.engine — инфраструктурный движок (подкапотная магия).

Содержит модули, которые нужны для сборки бота, но не используются
разработчиком фичи в повседневной работе.

Подмодули:
    engine.middlewares   — системные middleware (Throttling, Security, Container, …)
    engine.discovery     — FeatureDiscoveryService (авто-обнаружение фич)
    engine.factory       — BotBuilder, compile_locales
    engine.router_builder — collect_feature_routers, build_main_router
    engine.http          — BaseApiClient, ApiClientError
"""
