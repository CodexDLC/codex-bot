from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from aiogram.types import Chat, Message, User

from codex_bot.engine.middlewares.throttling import ThrottlingMiddleware


@pytest.fixture
def middleware(mock_redis):
    return ThrottlingMiddleware(redis=mock_redis, rate_limit=1.0)


@pytest.fixture
def mock_handler():
    return AsyncMock(return_value="handler_result")


@pytest.fixture
def mock_event():
    user = User(id=123, is_bot=False, first_name="Test")
    chat = Chat(id=456, type="private")
    # Aiogram 3.x Message requires a valid date (datetime object)
    return Message(message_id=1, date=datetime.now(), chat=chat, from_user=user)


@pytest.mark.asyncio
async def test_throttling_allowed(middleware, mock_redis, mock_event, mock_handler):
    # Redis set nx returns True (not throttled)
    mock_redis.set = AsyncMock(return_value=True)

    result = await middleware(mock_handler, mock_event, {})

    assert result == "handler_result"
    mock_redis.set.assert_called_once()
    mock_handler.assert_called_once()


@pytest.mark.asyncio
async def test_throttling_blocked(middleware, mock_redis, mock_event, mock_handler):
    # Redis set nx returns False (throttled)
    mock_redis.set = AsyncMock(return_value=False)

    result = await middleware(mock_handler, mock_event, {})

    assert result is None
    mock_redis.set.assert_called_once()
    mock_handler.assert_not_called()


@pytest.mark.asyncio
async def test_throttling_no_user(middleware, mock_redis, mock_handler):
    # Event without from_user should not be throttled
    chat = Chat(id=456, type="private")
    event = Message(message_id=1, date=datetime.now(), chat=chat)

    result = await middleware(mock_handler, event, {})

    assert result == "handler_result"
    mock_redis.set.assert_not_called()
    mock_handler.assert_called_once()
