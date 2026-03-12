from unittest.mock import AsyncMock, MagicMock

import pytest


def pytest_collection_modifyitems(items):
    """
    Automatically marks all tests as 'unit' if they are not marked as 'integration'.
    This ensures that CI and local quality tools pick them up by default.
    """
    for item in items:
        if "integration" not in item.keywords:
            item.add_marker(pytest.mark.unit)


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.send_message = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.send_animation = AsyncMock()
    bot.edit_message_media = AsyncMock()
    return bot


@pytest.fixture
def mock_fsm_context():
    state = AsyncMock()
    state.get_state = AsyncMock(return_value="test_state")
    state.set_state = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.update_data = AsyncMock()
    state.set_data = AsyncMock()
    state.clear = AsyncMock()
    return state


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock()
    redis.set = AsyncMock()
    redis.delete = AsyncMock()
    redis.exists = AsyncMock()
    return redis


@pytest.fixture
def mock_container():
    container = MagicMock()
    container.features = {}
    return container
