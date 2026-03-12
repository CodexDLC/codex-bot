"""
Universal Bot Runner — The main orchestrator for starting codex-bot services.

Handles logging initialization, Redis client creation, DI container setup,
and manages concurrent tasks like Telegram polling and Redis Stream listening.
"""

import asyncio
import logging
import sys
from collections.abc import Callable
from typing import Any

# We assume these might be optional or imported from the project
# but we provide a standard interface.


async def _run_services(
    settings: Any,
    container_class: type,
    bot_factory: Callable[..., Any],
    setup_logging_func: Callable[..., Any] | None = None,
) -> None:
    """Internal async runner for bot services."""

    # 1. Initialize Logging
    if setup_logging_func:
        setup_logging_func(settings)
    else:
        logging.basicConfig(
            level=logging.DEBUG if getattr(settings, "debug", False) else logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    log = logging.getLogger("codex_bot.runner")
    log.info("Starting application...")

    # 2. Initialize Infrastructure (Redis)
    redis_client = None
    # We check for generic use_redis or more granular flags
    use_redis = (
        getattr(settings, "use_redis", False)
        or getattr(settings, "use_redis_fsm", False)
        or getattr(settings, "use_redis_streams", False)
    )

    if use_redis:
        from redis.asyncio import Redis

        redis_client = Redis.from_url(
            getattr(settings, "redis_url", "redis://localhost:6379/0"),
            encoding="utf-8",
            decode_responses=True,
        )
        log.info("Redis client initialized.")

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
                allowed_updates=getattr(settings, "bot_allowed_updates", ["message", "callback_query", "inline_query"]),
            )
        )

        # Task B: Redis Streams (if enabled)
        if getattr(settings, "use_redis_streams", False) and hasattr(container, "stream_processor"):
            tasks.append(container.stream_processor.start_listening())
            log.info("Redis Stream listener added to event loop.")

        # 6. Run Everything
        log.info("Services launched. Press Ctrl+C to stop.")
        await asyncio.gather(*tasks)

    except asyncio.CancelledError:
        log.info("Cancellation received.")
    except Exception as e:
        log.exception(f"Critical error during execution: {e}")
        raise
    finally:
        log.info("Shutting down infrastructure...")
        if "container" in locals():
            await container.shutdown()

        if redis_client:
            await redis_client.aclose()
            log.info("Redis connection closed.")


def run_bot_app(
    settings: Any,
    container_class: type,
    bot_factory: Callable[..., Any],
    setup_logging_func: Callable[..., Any] | None = None,
) -> None:
    """
    Synchronous entry point to start the bot application.

    Usage:
        run_bot_app(settings, BotContainer, build_bot, setup_logging)
    """
    try:
        asyncio.run(_run_services(settings, container_class, bot_factory, setup_logging_func))
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Bot stopped by user.")
    except Exception as e:
        print(f"\n🔥 Fatal error: {e}")
        sys.exit(1)
