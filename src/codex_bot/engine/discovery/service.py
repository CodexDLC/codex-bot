"""
FeatureDiscoveryService — Auto-discovery and registration of features.

Supports two modes of operation:
1. **Auto-discovery** — scans modules from a list of feature_paths via importlib.
2. **Explicit registration** — the developer passes objects directly (fallback for
   environments without dynamic imports: PyInstaller, strict mypy, etc.).

Both modes can be combined in a single application.
"""

import importlib
import logging
from types import ModuleType
from typing import Any, cast

from aiogram import Router

from ...fsm.garbage_collector import GarbageStateRegistry
from ...redis.dispatcher import BotRedisDispatcher
from ...redis.router import RedisRouter

log = logging.getLogger(__name__)


class FeatureDiscoveryService:
    """
    Service for discovering and registering feature configurations.

    Two modes:

    **Mode 1: Auto-discovery** (similar to Django's INSTALLED_APPS):
    ```python
    discovery = FeatureDiscoveryService(
        module_prefix="src.telegram_bot",
        installed_features=["features.telegram.commands", "features.telegram.booking"],
        installed_redis_features=["features.redis.notifications"],
        redis_dispatcher=bot_redis_dispatcher,
    )
    discovery.discover_all()
    orchestrators = discovery.create_feature_orchestrators(container)
    ```

    **Mode 2: Explicit registration** (fallback):
    ```python
    discovery = FeatureDiscoveryService()
    discovery.register_router(commands_router)
    discovery.register_orchestrator("booking", BookingOrchestrator(container))
    discovery.register_garbage_states(BookingStates)
    ```

    Args:
        module_prefix: Module path prefix for auto-discovery.
                       Example: "src.telegram_bot".
        installed_features: List of Telegram feature paths (with Aiogram routers).
        installed_redis_features: List of Redis feature paths (with RedisRouter).
        redis_dispatcher: Dispatcher for registering Redis handlers.
    """

    def __init__(
        self,
        module_prefix: str = "",
        installed_features: list[str] | None = None,
        installed_redis_features: list[str] | None = None,
        redis_dispatcher: BotRedisDispatcher | None = None,
    ) -> None:
        self._prefix = module_prefix
        self._features = installed_features or []
        self._redis_features = installed_redis_features or []
        self._redis_dispatcher = redis_dispatcher

        # Explicitly registered objects (Mode 2)
        self._explicit_routers: list[Router] = []
        self._explicit_orchestrators: dict[str, Any] = {}

    # =========================================================================
    # Mode 1: Auto-discovery
    # =========================================================================

    def discover_all(self) -> None:
        """
        Starts auto-discovery of all registered features.

        For Telegram features: loads menu config, garbage states, Aiogram routers.
        For Redis features: loads RedisRouter and connects it to the dispatcher.
        """
        for feature_path in self._features:
            self._discover_menu(feature_path)
            self._discover_garbage_states(feature_path)

        for feature_path in self._redis_features:
            self._discover_redis_handlers(feature_path)
            self._discover_garbage_states(feature_path)

    def create_feature_orchestrators(self, container: Any) -> dict[str, Any]:
        """
        Creates orchestrators for all features via their factory functions.

        Looks for the `create_orchestrator(container)` function in the `feature_setting.py`
        of each feature. The key prefix for Redis features is "redis_".

        Args:
            container: Project's DI container.

        Returns:
            Dictionary {feature_key: orchestrator_instance}.
        """
        orchestrators = dict(self._explicit_orchestrators)
        configs = [(self._features, ""), (self._redis_features, "redis_")]

        for feature_list, prefix in configs:
            for feature_path in feature_list:
                module = self._load_feature_module(feature_path)
                if not module:
                    continue
                factory = getattr(module, "create_orchestrator", None)
                if not factory:
                    continue
                base_name = feature_path.split(".")[-1]
                key = f"{prefix}{base_name}"
                orchestrators[key] = factory(container)
                log.info(f"FeatureDiscovery | orchestrator loaded key='{key}'")

        return orchestrators

    def collect_aiogram_routers(self) -> list[Router]:
        """
        Collects Aiogram Routers from all Telegram features.

        Returns:
            List of Routers to be included in the main router.
        """
        routers = list(self._explicit_routers)

        for feature_path in self._features:
            module_path = f"{self._prefix}.{feature_path}.handlers" if self._prefix else f"{feature_path}.handlers"
            try:
                module = importlib.import_module(module_path)
                router = getattr(module, "router", None)
                if router and isinstance(router, Router):
                    routers.append(router)
                    log.info(f"FeatureDiscovery | router loaded feature='{feature_path}'")
            except ImportError as e:
                if getattr(e, "name", None) == module_path:
                    log.debug(f"FeatureDiscovery | no handlers file feature='{feature_path}'")
                else:
                    log.critical(f"FeatureDiscovery | Broken import inside '{feature_path}': {e}")
                    raise

        return routers

    def get_menu_buttons(self, is_admin: bool | None = None) -> dict[str, dict[str, Any]]:
        """
        Returns menu button configurations for all Telegram features.

        Args:
            is_admin: None — all buttons, True — only admin, False — only user.

        Returns:
            Dictionary {feature_key: menu_config_dict}.
        """
        buttons: dict[str, dict[str, Any]] = {}
        for feature_path in self._features:
            btn = self._discover_menu(feature_path)
            if btn:
                if is_admin is not None and btn.get("is_admin", False) != is_admin:
                    continue
                key = btn.get("key", feature_path)
                buttons[key] = btn
        return buttons

    # =========================================================================
    # Mode 2: Explicit registration (fallback)
    # =========================================================================

    def register_router(self, router: Router) -> None:
        """
        Explicitly registers an Aiogram Router (without auto-discovery).

        Args:
            router: Instance of aiogram.Router.
        """
        self._explicit_routers.append(router)

    def register_orchestrator(self, key: str, orchestrator: Any) -> None:
        """
        Explicitly registers a feature orchestrator.

        Args:
            key: Feature key (e.g., "booking", "redis_notifications").
            orchestrator: Orchestrator instance.
        """
        self._explicit_orchestrators[key] = orchestrator

    def register_garbage_states(self, states: Any) -> None:
        """
        Explicitly registers states as garbage (Garbage Collector).

        Args:
            states: State, StatesGroup, string, or a list of them.
        """
        GarbageStateRegistry.register(states)

    # =========================================================================
    # Private auto-discovery methods
    # =========================================================================

    def _load_feature_module(self, feature_path: str) -> ModuleType | None:
        candidates = []
        if self._prefix:
            candidates.append(f"{self._prefix}.{feature_path}.feature_setting")
            candidates.append(f"{self._prefix}.{feature_path}")
        candidates.append(f"{feature_path}.feature_setting")
        candidates.append(feature_path)

        for path in candidates:
            try:
                return importlib.import_module(path)
            except ImportError:
                continue
        return None

    def _discover_menu(self, feature_path: str) -> dict[str, Any] | None:
        module = self._load_feature_module(feature_path)
        if module:
            config = getattr(module, "MENU_CONFIG", None)
            if config and isinstance(config, dict):
                return cast(dict[str, Any] | None, config)
        return None

    def _discover_garbage_states(self, feature_path: str) -> None:
        module = self._load_feature_module(feature_path)
        if not module:
            return
        garbage = getattr(module, "GARBAGE_STATES", None)
        if garbage:
            GarbageStateRegistry.register(garbage)
            return
        if getattr(module, "GARBAGE_COLLECT", False):
            states = getattr(module, "STATES", None)
            if states:
                GarbageStateRegistry.register(states)

    def _discover_redis_handlers(self, feature_path: str) -> None:
        if not self._redis_dispatcher:
            return
        module_path = f"{self._prefix}.{feature_path}.handlers" if self._prefix else f"{feature_path}.handlers"
        try:
            module = importlib.import_module(module_path)
            redis_router = getattr(module, "redis_router", None)
            if redis_router and isinstance(redis_router, RedisRouter):
                self._redis_dispatcher.include_router(redis_router)
        except ImportError as e:
            if getattr(e, "name", None) == module_path:
                log.debug(f"FeatureDiscovery | no redis handlers file feature='{module_path}'")
            else:
                log.critical(f"FeatureDiscovery | Broken import inside '{module_path}': {e}")
                raise
