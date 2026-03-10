from typing import Any

from loguru import logger as log
from codex_bot.redis import RedisRouter

# Router for events from Redis Stream
redis_router = RedisRouter()


@redis_router.message("your_event_type")
async def handle_{feature_key}_event(message_data: dict[str, Any], container: Any):
    """Handler for {class_name} events from Redis Stream.

    Do NOT catch exceptions here — let them propagate to the dispatcher.
    The dispatcher will trigger the retry scheduler if configured.
    """
    log.info(f"{class_name} | Processing event type='{message_data.get('type')}'")

    orchestrator = container.{container_key}
    view_sender = container.view_sender

    # Processing logic:
    # view_dto = await orchestrator.handle_event(message_data)
    # await view_sender.send(view_dto)
