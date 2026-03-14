"""
Universal Bot Runner — The entry point for library service orchestration.

The runner manages the high-level application lifecycle, including
infrastructure bootstrap, DI container initialization, and concurrent
task management (Polling vs. Streams).
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any, Protocol

from aiogram import Bot, Dispatcher

log = logging.getLogger("codex_bot.runner")


class BotSettingsProtocol(Protocol):
    """Minimum requirements for the settings object."""

    debug: bool
    use_redis: bool
    use_redis_fsm: bool
    use_redis_streams: bool
    redis_url: str
    bot_allowed_updates: list[str]


class ContainerProtocol(Protocol):
    """Interface for the dependency injection container."""

    @property
    def stream_processor(self) -> Any: ...
    def set_bot(self, bot: Bot) -> None: ...
    async def shutdown(self) -> None: ...


# Type for the bot factory returning (Bot, Dispatcher)
BotFactoryType = Callable[[BotSettingsProtocol, Any, ContainerProtocol], tuple[Bot, Dispatcher]]


async def _run_services(
    settings: BotSettingsProtocol,
    container_class: Callable[[BotSettingsProtocol, Any], ContainerProtocol],
    bot_factory: BotFactoryType,
    setup_logging_func: Callable[[BotSettingsProtocol], None] | None = None,
) -> None:
    """Internal async runner for bot services."""

    # 1. Initialize Logging
    if setup_logging_func:
        setup_logging_func(settings)
    else:
        logging.basicConfig(
            level=logging.DEBUG if settings.debug else logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    log.info("Starting application...")

    # 2. Initialize Infrastructure (Redis)
    redis_client = None
    use_redis = settings.use_redis or settings.use_redis_fsm or settings.use_redis_streams

    if use_redis:
        from redis.asyncio import Redis

        redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        log.info("Redis client initialized.")

    container: ContainerProtocol | None = None
    try:
        # 3. Initialize DI Container
        container = container_class(settings, redis_client)
        log.info(f"Container '{container_class.__name__}' initialized.")

        # 4. Build Bot and Dispatcher
        bot, dp = bot_factory(settings, redis_client, container)
        container.set_bot(bot)
        log.info("Bot and Dispatcher ready.")

        # 5. Assemble background tasks
        tasks = []

        # Task A: Main Telegram Polling
        tasks.append(
            dp.start_polling(
                bot,
                allowed_updates=settings.bot_allowed_updates,
            )
        )

        # Task B: Redis Streams (if enabled)
        if settings.use_redis_streams:
            # Check if container actually implements the processor
            processor = getattr(container, "stream_processor", None)
            if processor and hasattr(processor, "start_listening"):
                tasks.append(processor.start_listening())
                log.info("Redis Stream listener added to event loop.")
            else:
                log.warning("use_redis_streams is True but container has no stream_processor!")

        # 6. Run Everything
        log.info("Services launched. Press Ctrl+C to stop.")
        await asyncio.gather(*tasks)

    except asyncio.CancelledError:
        log.info("Cancellation received. Shutting down gracefully...")
    except Exception as e:
        log.exception(f"Critical error during execution: {e}")
        raise
    finally:
        log.info("Shutting down infrastructure...")
        if container:
            await container.shutdown()

        if redis_client:
            await redis_client.aclose()
            log.info("Redis connection closed.")


def run_bot_app(
    settings: BotSettingsProtocol,
    container_class: Callable[[BotSettingsProtocol, Any], ContainerProtocol],
    bot_factory: BotFactoryType,
    setup_logging_func: Callable[[BotSettingsProtocol], None] | None = None,
) -> None:
    """Synchronous entry point for application execution.

    Wraps the asynchronous lifecycle runner and handles termination signals
    (KeyboardInterrupt, SystemExit) to ensure a clean exit.

    Args:
        settings: Application configuration object.
        container_class: Factory for the DI container.
        bot_factory: Callable returning a configured `Bot` and `Dispatcher`.
        setup_logging_func: Optional callback for custom logging configuration.

    Raises:
        Exception: Re-raises critical errors encountered during the bot's runtime.
    """
    try:
        asyncio.run(_run_services(settings, container_class, bot_factory, setup_logging_func))
    except (KeyboardInterrupt, SystemExit):
        log.info("👋 Bot stopped by user/system.")
    except Exception as e:
        log.critical("🔥 Fatal error occurred in the bot lifecycle.", exc_info=e)
        raise
