"""
codex_bot.stream.dispatcher
=============================
Bot-specific Stream dispatcher with DI container support.
"""

from typing import Any

from codex_platform.streams import (
    RetrySchedulerProtocol,
    StreamDispatcher,
)


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
