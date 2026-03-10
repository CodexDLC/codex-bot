from unittest.mock import MagicMock

from aiogram.fsm.storage.memory import MemoryStorage

from codex_bot.engine.factory.bot_builder import BotBuilder


def test_bot_builder_init():
    # pragma: allowlist secret
    builder = BotBuilder(bot_token="123:ABC")
    assert builder._bot_token == "123:ABC"
    assert isinstance(builder._fsm_storage, MemoryStorage)


def test_bot_builder_custom_storage():
    # pragma: allowlist secret
    storage = MagicMock()
    builder = BotBuilder(bot_token="123:ABC", fsm_storage=storage)
    assert builder._fsm_storage == storage


def test_bot_builder_add_middleware():
    # pragma: allowlist secret
    builder = BotBuilder(bot_token="123:ABC")
    middleware = MagicMock()

    builder.add_middleware(middleware)
    assert middleware in builder._middlewares


def test_bot_builder_chaining():
    # pragma: allowlist secret
    builder = BotBuilder(bot_token="123:ABC")
    middleware = MagicMock()

    res = builder.add_middleware(middleware)
    assert res == builder
