"""
codex_bot.stream.router
========================
Bot-specific Stream router. Extends StreamRouter from codex-platform.

Currently identical to StreamRouter — FSM integration will be added later.
All existing feature handlers using ``redis_router = BotStreamRouter()`` will
continue to work without changes when FSM support is added.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from codex_platform.stream_broker import (
        BaseStreamRouter as StreamRouter,
    )
else:
    try:
        from codex_platform.stream_broker import (
            BaseStreamRouter as StreamRouter,
        )
    except ImportError:
        # Failsafe for environment without codex-platform
        class StreamRouter:
            def include_router(self, *args: Any, **kwargs: Any) -> Any:
                pass

            def on(self, *args: Any, **kwargs: Any) -> Any:
                def decorator(func: Any) -> Any:
                    return func

                return decorator


class BotStreamRouter(StreamRouter):  # type: ignore
    """
    Stream event router for codex_bot features.

    Extends ``StreamRouter`` with bot-specific capabilities (FSM, DI).
    Currently a pass-through — FSM state support will be added here later.

    Usage in feature handlers::

        from codex_bot.stream import BotStreamRouter

        redis_router = BotStreamRouter()

        @redis_router.on("booking.confirmed")
        async def handle_booking(payload: dict) -> None:
            ...
    """

    # TODO: override on() to support state= and state_key= parameters
    # TODO: inject FSMContext into handler signature based on state_key from payload
