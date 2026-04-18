"""
FeatureDiscoveryService — Auto-discovery and registration of features.

Strictly follows the convention:
- Telegram features: features.telegram.{name}.feature_setting
- Redis features:    features.redis.{name}.feature_setting
"""

import importlib
import logging
from types import ModuleType
from typing import Any, Literal

from aiogram import Router

try:
    from codex_platform.stream_broker import StreamRouter  # type: ignore[import-not-found]
except ImportError:

    class StreamRouter:  # type: ignore
        pass


from ...fsm.garbage_collector import GarbageStateRegistry
from ...stream.dispatcher import BotStreamDispatcher

log = logging.getLogger(__name__)


class FeatureDiscoveryService:
    """Automated orchestration for framework-wide feature registration.

    Operates on a 'convention over configuration' principle to dynamically
    locate and initialize business features. Manages the discovery of
    Aiogram routers, Redis stream handlers, UI menu configurations, and
    FSM garbage collection states.
    """

    def __init__(
        self,
        module_prefix: str = "features",
        installed_features: list[str] | None = None,
        installed_redis_features: list[str] | None = None,
        redis_dispatcher: BotStreamDispatcher | None = None,
    ) -> None:
        """
        Initializes the discovery service.

        Args:
            module_prefix: Base package for features (default: "features").
            installed_features: Simple folder names of Telegram features.
            installed_redis_features: Simple folder names of Redis features.
            redis_dispatcher: Dispatcher for registering Redis handlers.
        """
        self._prefix = module_prefix
        self._features = installed_features or []
        self._redis_features = installed_redis_features or []
        self._redis_dispatcher = redis_dispatcher

        # Explicitly registered objects (fallback for non-dynamic environments)
        self._explicit_routers: list[Router] = []
        self._explicit_orchestrators: dict[str, Any] = {}

    def discover_all(self) -> None:
        """
        Starts auto-discovery of all registered features based on convention.

        For Telegram features: loads menu config, garbage states, Aiogram routers.
        For Redis features: loads RedisRouter and connects it to the dispatcher.
        """
        for name in self._features:
            module = self._load_module(name, "telegram")
            if module:
                self._register_menu(module, name)
                self._register_garbage(module)

        for name in self._redis_features:
            module = self._load_module(name, "redis")
            if module:
                self._register_redis_handlers(module, name)
                self._register_garbage(module)

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

        configs: list[tuple[list[str], Literal["telegram", "redis"], str]] = [
            (self._features, "telegram", ""),
            (self._redis_features, "redis", "redis_"),
        ]

        for names, f_type, key_prefix in configs:
            for name in names:
                module = self._load_module(name, f_type)
                if not module:
                    continue

                factory = getattr(module, "create_orchestrator", None)
                if factory and callable(factory):
                    key = f"{key_prefix}{name}"
                    orchestrators[key] = factory(container)
                    log.info(f"FeatureDiscovery | Orchestrator loaded: {key}")

        return orchestrators

    def collect_aiogram_routers(self) -> list[Router]:
        """
        Collects Aiogram Routers from all Telegram features.

        Expects routers to be named 'router' in '{name}.handlers.handlers'.

        Returns:
            List of Routers to be included in the main dispatcher.
        """
        routers = list(self._explicit_routers)

        for name in self._features:
            path = f"{self._prefix}.telegram.{name}.handlers"
            try:
                module = importlib.import_module(path)
                router = getattr(module, "router", None)
                if isinstance(router, Router):
                    routers.append(router)
                    log.info(f"FeatureDiscovery | Router loaded: {name}")
            except ImportError:
                log.debug(f"FeatureDiscovery | No handlers found for {name} at {path}")
                continue

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
        for name in self._features:
            module = self._load_module(name, "telegram")
            if module:
                btn = getattr(module, "MENU_CONFIG", None)
                if isinstance(btn, dict):
                    if is_admin is not None and btn.get("is_admin", False) != is_admin:
                        continue
                    buttons[btn.get("key", name)] = btn
        return buttons

    # =========================================================================
    # Explicit Registration (Fallback)
    # =========================================================================

    def register_router(self, router: Router) -> None:
        """Explicitly registers an Aiogram Router."""
        self._explicit_routers.append(router)

    def register_orchestrator(self, key: str, orchestrator: Any) -> None:
        """Explicitly registers a feature orchestrator."""
        self._explicit_orchestrators[key] = orchestrator

    def register_garbage_states(self, states: Any) -> None:
        """Explicitly registers states for the Garbage Collector."""
        GarbageStateRegistry.register(states)

    # =========================================================================
    # Internal Logic
    # =========================================================================

    def _load_module(self, name: str, f_type: Literal["telegram", "redis"]) -> ModuleType | None:
        """Loads the feature_setting module following the convention."""
        path = f"{self._prefix}.{f_type}.{name}.feature_setting"
        try:
            return importlib.import_module(path)
        except ImportError:
            return None

    def _register_menu(self, module: ModuleType, name: str) -> None:
        """Internal helper to extract menu config."""
        pass

    def _register_garbage(self, module: ModuleType) -> None:
        """Registers states for the Garbage Collector."""
        garbage = getattr(module, "GARBAGE_STATES", None)
        if garbage:
            GarbageStateRegistry.register(garbage)
            return

        if getattr(module, "GARBAGE_COLLECT", False):
            states = getattr(module, "STATES", None)
            if states:
                GarbageStateRegistry.register(states)

    def _register_redis_handlers(self, module: ModuleType, name: str) -> None:
        """Connects RedisRouter to the dispatcher."""
        if not self._redis_dispatcher:
            return

        path = f"{self._prefix}.redis.{name}.handlers"
        try:
            handler_module = importlib.import_module(path)
            router = getattr(handler_module, "redis_router", None)
            if isinstance(router, StreamRouter):
                self._redis_dispatcher.include_router(router)
        except ImportError:
            pass
