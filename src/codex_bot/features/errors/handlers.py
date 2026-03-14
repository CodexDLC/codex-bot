"""
Redis Error Handlers — Asynchronous event consumption for system errors.

Registers specialized Redis Stream handlers for 'system_error' events.
Integrates with the framework's `RedisRouter` to provide automated,
container-aware error propagation to the end user.
"""

from __future__ import annotations

import logging
from typing import Any

from codex_bot.redis.router import RedisRouter

from .orchestrator import ErrorOrchestrator

log = logging.getLogger(__name__)

redis_router = RedisRouter()


@redis_router.message("system_error")
async def handle_system_error(
    message_data: dict[str, Any],
    container: Any,
) -> None:
    """Handle a ``system_error`` event from the Redis Stream.

    Delegates to ``container.errors_orchestrator.handle_error()`` and
    sends the rendered view via ``container.view_sender``.

    Silently skips if ``errors_orchestrator`` or ``view_sender`` is not
    present on the container (feature not configured).

    Args:
        message_data: Raw dict from the Redis Stream message.
        container: Bot dependency container. Must have ``errors_orchestrator``
                   and ``view_sender`` attributes.
    """
    orchestrator: ErrorOrchestrator | None = getattr(container, "errors_orchestrator", None)
    if orchestrator is None:
        log.debug("ErrorHandler | errors_orchestrator not configured, skipping")
        return

    view_sender = getattr(container, "view_sender", None)
    if view_sender is None:
        log.debug("ErrorHandler | view_sender not configured, skipping")
        return

    log.debug("ErrorHandler | processing system_error event")
    view = orchestrator.handle_error(message_data)

    if not view.session_key or not view.chat_id:
        log.warning("ErrorHandler | missing user_id or chat_id in message_data, cannot send error UI")
        return

    await view_sender.send(view)
