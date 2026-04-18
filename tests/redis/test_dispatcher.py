"""
Tests for BotRedisDispatcher event orchestration.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from codex_bot.redis.dispatcher import BotRedisDispatcher
from codex_bot.redis.router import RedisRouter


@pytest.fixture
def mock_container():
    container = MagicMock()
    container.bot = MagicMock()
    return container


@pytest.fixture
def dispatcher():
    return BotRedisDispatcher()


@pytest.mark.asyncio
async def test_dispatcher_process_message_success(dispatcher, mock_container):
    handler = AsyncMock()
    dispatcher.setup(container=mock_container)
    dispatcher.on_message("test.type")(handler)

    await dispatcher.process_message({"type": "test.type", "data": 1})

    handler.assert_called_once_with({"type": "test.type", "data": 1}, mock_container)


@pytest.mark.asyncio
async def test_dispatcher_include_router(dispatcher, mock_container):
    router = RedisRouter()
    handler = AsyncMock()
    router.message("router.type")(handler)

    dispatcher.setup(container=mock_container)
    dispatcher.include_router(router)

    await dispatcher.process_message({"type": "router.type"})
    handler.assert_called_once()


@pytest.mark.asyncio
async def test_dispatcher_retry_scheduling(mock_container):
    scheduler = AsyncMock()
    dispatcher = BotRedisDispatcher(retry_scheduler=scheduler)
    dispatcher.setup(container=mock_container)

    handler = AsyncMock(side_effect=Exception("Fail"))
    dispatcher.on_message("fail.type")(handler)

    payload = {"type": "fail.type"}
    await dispatcher.process_message(payload)

    scheduler.schedule_retry.assert_called_once()
