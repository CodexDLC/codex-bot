"""
codex_bot.stream.dispatcher
=============================
Bot-specific Stream dispatcher with DI container support.
"""

from typing import Any

try:
    from codex_platform.stream_broker import RetrySchedulerProtocol, StreamDispatcher  # type: ignore[import-not-found]
except ImportError:
    # Failsafe for environment without codex-platform
    class RetrySchedulerProtocol:  # type: ignore
        pass

    class StreamDispatcher:  # type: ignore
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        async def process(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("codex-platform is not installed")

        def include_router(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("codex-platform is not installed")


class BotStreamDispatcher(StreamDispatcher):  # type: ignore
    """
    Stream dispatcher for codex_bot with DI container injection.

    Extends ``StreamDispatcher`` adding bot's DI container.
    Call ``setup(container)`` before starting the processor.

    Usage::

        dispatcher = BotStreamDispatcher()
        dispatcher.setup(container)

        processor.set_callback(dispatcher.process)
        await processor.start()
    """

    def __init__(self, retry_scheduler: RetrySchedulerProtocol | None = None) -> None:
        super().__init__(retry_scheduler)
        self._container: Any | None = None

    def setup(self, container: Any) -> None:
        """Sets the DI container. Call before starting the processor."""
        self._container = container
