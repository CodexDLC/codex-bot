from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from aiogram.types import TelegramObject, User

from codex_bot.engine.middlewares.i18n import FSMContextI18nManager


@pytest.fixture
def state():
    fsm_state = AsyncMock()
    fsm_state.get_data = AsyncMock(return_value={})
    fsm_state.set_data = AsyncMock()
    return fsm_state


def test_manager_initialization():
    manager = FSMContextI18nManager(default_locale="de")

    assert hasattr(manager, "locale_getter") is True
    assert hasattr(manager, "locale_setter") is True
    assert manager.default_locale == "de"


async def test_get_locale_prefers_fsm_locale(state):
    state.get_data.return_value = {"locale": "ru"}
    manager = FSMContextI18nManager(allowed_locales=["de"], default_locale="de")

    locale = await manager.get_locale(state=state)

    assert locale == "ru"


async def test_get_locale_uses_allowed_telegram_language(state):
    user = User(id=1, is_bot=False, first_name="Test", language_code="ru")
    manager = FSMContextI18nManager(allowed_locales=["ru", "de"], default_locale="de")

    locale = await manager.get_locale(event_from_user=user, state=state)

    assert locale == "ru"


async def test_get_locale_falls_back_for_disallowed_language(state):
    user = User(id=1, is_bot=False, first_name="Test", language_code="en")
    manager = FSMContextI18nManager(allowed_locales=["ru", "de"], default_locale="de")

    locale = await manager.get_locale(event_from_user=user, state=state)

    assert locale == "de"


async def test_get_locale_uses_default_without_state_or_user():
    manager = FSMContextI18nManager(default_locale="de")

    locale = await manager.get_locale()

    assert locale == "de"


async def test_set_locale_writes_to_fsm_storage(state):
    state.get_data.return_value = {}
    manager = FSMContextI18nManager(default_locale="de")

    await manager.set_locale("ru", state=state)

    state.set_data.assert_called_once_with({"locale": "ru"})


async def test_aiogram_i18n_middleware_uses_manager_locale_getter(tmp_path: Path, state):
    from aiogram_i18n import I18nMiddleware
    from aiogram_i18n.cores import FluentRuntimeCore

    locale_dir = tmp_path / "de"
    locale_dir.mkdir()
    (locale_dir / "messages.ftl").write_text("hello = Hallo\n", encoding="utf-8")

    manager = FSMContextI18nManager(default_locale="de")
    middleware = I18nMiddleware(
        core=FluentRuntimeCore(path=tmp_path / "{locale}"),
        manager=manager,
        default_locale="de",
    )

    event = TelegramObject()
    handler = AsyncMock(return_value="ok")

    result = await middleware(handler, event, {"state": state})

    assert result == "ok"
    handler.assert_awaited_once()
