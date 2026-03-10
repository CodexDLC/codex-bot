import pytest
from aiogram.types import InlineKeyboardMarkup
from pydantic import ValidationError

from codex_bot.base.view_dto import MessageCoordsDTO, UnifiedViewDTO, ViewResultDTO


def test_view_result_dto_minimal():
    view = ViewResultDTO(text="Hello")
    assert view.text == "Hello"
    assert view.kb is None


def test_view_result_dto_full():
    kb = InlineKeyboardMarkup(inline_keyboard=[])
    view = ViewResultDTO(text="Hello", kb=kb)
    assert view.text == "Hello"
    assert view.kb == kb


def test_unified_view_dto_minimal():
    content = ViewResultDTO(text="Content")
    unified = UnifiedViewDTO(content=content)
    assert unified.content.text == "Content"
    assert unified.chat_id is None
    assert unified.session_key is None


def test_unified_view_dto_full():
    content = ViewResultDTO(text="Content")
    menu = ViewResultDTO(text="Menu")
    unified = UnifiedViewDTO(content=content, menu=menu, chat_id=12345, session_key="user:12345")
    assert unified.content.text == "Content"
    assert unified.menu.text == "Menu"
    assert unified.chat_id == 12345
    assert unified.session_key == "user:12345"


def test_message_coords_dto():
    coords = MessageCoordsDTO(chat_id=123, message_id=456)
    assert coords.chat_id == 123
    assert coords.message_id == 456


def test_view_result_dto_validation_error():
    with pytest.raises(ValidationError):
        # text is required
        ViewResultDTO()  # type: ignore
