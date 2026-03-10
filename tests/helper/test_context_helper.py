from datetime import datetime

import pytest
from aiogram.types import CallbackQuery, Chat, Message, User

from codex_bot.base.context_dto import BaseBotContext
from codex_bot.helper.context_helper import ContextHelper


@pytest.fixture
def mock_user():
    return User(id=123, is_bot=False, first_name="Test", username="testuser")


@pytest.fixture
def mock_chat():
    return Chat(id=456, type="private")


def test_extract_base_context_from_message(mock_user, mock_chat):
    message = Message(message_id=1, date=datetime.now(), chat=mock_chat, from_user=mock_user)
    ctx = ContextHelper.extract_base_context(message)

    assert isinstance(ctx, BaseBotContext)
    assert ctx.user_id == 123
    assert ctx.chat_id == 456
    assert ctx.message_id == 1


def test_extract_base_context_from_callback(mock_user, mock_chat):
    message = Message(message_id=1, date=datetime.now(), chat=mock_chat, from_user=mock_user)
    callback = CallbackQuery(id="1", from_user=mock_user, chat_instance="1", message=message)

    ctx = ContextHelper.extract_base_context(callback)

    assert ctx.user_id == 123
    assert ctx.chat_id == 456
    assert ctx.message_id == 1


def test_extract_base_context_no_user(mock_chat):
    # Fallback to chat_id if user is missing
    message = Message(message_id=1, date=datetime.now(), chat=mock_chat)
    ctx = ContextHelper.extract_base_context(message)

    assert ctx.user_id == 456
    assert ctx.chat_id == 456
