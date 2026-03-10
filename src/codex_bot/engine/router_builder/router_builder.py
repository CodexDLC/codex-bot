"""
RouterBuilder — Parametric assembly of the main Aiogram router.

Replaces hardcoded core/routers.py with explicit parameters
module_prefix and installed_features.

Fail Fast Principle: if a feature is declared in installed_features and its handlers.py
contains an error — the startup fails immediately, rather than silently ignoring the problem.
"""

from __future__ import annotations

import importlib
import logging

from aiogram import Router

log = logging.getLogger(__name__)


def collect_feature_routers(
    installed_features: list[str],
    module_prefix: str = "",
    handler_module: str = "handlers",
) -> list[Router]:
    """Collects Aiogram routers from feature modules.

    For each feature in ``installed_features``, it attempts to import
    ``{module_prefix}.{feature_path}.{handler_module}``
    and extract the ``router`` attribute from it.

    **Fail Fast:** ``ImportError`` (no handlers file) — silent skip.
    Any other error (syntax, runtime) — exception propagates up, the bot does not start.

    Args:
        installed_features: List of paths to features
            (e.g., ``["features.telegram.booking", "features.telegram.profile"]``).
        module_prefix: Module prefix
            (e.g., ``"myproject"`` → ``"myproject.features.telegram.booking.handlers"``).
            Empty string — ``feature_path`` is used directly.
        handler_module: Name of the module with the router (default is ``"handlers"``).

    Returns:
        List of found ``Router`` objects.

    Raises:
        Exception: Any module loading error except ``ImportError`` (no file).

    Example:
        ```python
        routers = collect_feature_routers(
            installed_features=["features.telegram.booking", "features.telegram.profile"],
            module_prefix="myproject",
        )
        ```
    """
    routers: list[Router] = []

    for feature_path in installed_features:
        module_path = (
            f"{module_prefix}.{feature_path}.{handler_module}" if module_prefix else f"{feature_path}.{handler_module}"
        )

        try:
            module = importlib.import_module(module_path)
            feature_router = getattr(module, "router", None)
            if feature_router and isinstance(feature_router, Router):
                routers.append(feature_router)
                log.info(f"RouterBuilder | feature='{feature_path}' status=loaded")
            else:
                log.debug(f"RouterBuilder | feature='{feature_path}' status=no_router_attr")
        except ImportError as e:
            if getattr(e, "name", None) == module_path:
                # No handlers.py file — feature without UI, this is normal
                log.debug(f"RouterBuilder | feature='{feature_path}' status=no_handlers_file")
            else:
                # handlers.py exists, but there's a broken import inside — fail
                log.critical(f"RouterBuilder | Broken import inside '{feature_path}': {e}")
                raise
        # SyntaxError, NameError, etc. — not caught, the application fails immediately

    return routers


def build_main_router(
    installed_features: list[str],
    module_prefix: str = "",
    handler_module: str = "handlers",
    extra_routers: list[Router] | None = None,
    router_name: str = "main_router",
) -> Router:
    """Assembles the main application router.

    Creates a ``Router(name=router_name)``, includes routers from all features
    and additional routers (e.g., ``common_fsm_router``).

    Args:
        installed_features: List of paths to features.
        module_prefix: Module prefix (see ``collect_feature_routers``).
        handler_module: Name of the module with the router (default is ``"handlers"``).
        extra_routers: Additional routers included after features
            (e.g., ``[common_fsm_router]``).
        router_name: Name of the main router.

    Returns:
        The assembled ``Router``.

    Example:
        ```python
        from codex_bot.engine.router_builder import build_main_router
        from codex_bot.fsm import common_fsm_router

        main_router = build_main_router(
            installed_features=settings.INSTALLED_FEATURES,
            module_prefix="myproject",
            extra_routers=[common_fsm_router],
        )
        dp.include_router(main_router)
        ```
    """
    main_router = Router(name=router_name)
    feature_routers = collect_feature_routers(
        installed_features=installed_features,
        module_prefix=module_prefix,
        handler_module=handler_module,
    )

    all_routers: list[Router] = feature_routers + (extra_routers or [])
    if all_routers:
        main_router.include_routers(*all_routers)

    log.info(f"RouterBuilder | UI features loaded={len(feature_routers)} extra={len(extra_routers or [])}")
    return main_router
