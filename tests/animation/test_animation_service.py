from unittest.mock import AsyncMock, MagicMock

import pytest

from codex_bot.animation.animation_service import AnimationType, UIAnimationService
from codex_bot.base.view_dto import UnifiedViewDTO, ViewResultDTO


@pytest.fixture
def mock_sender():
    sender = MagicMock()
    sender.send = AsyncMock()
    return sender


@pytest.fixture
def animation_service(mock_sender):
    return UIAnimationService(sender=mock_sender)


def test_generate_progress_bar(animation_service):
    # 50% progress
    res = animation_service._generate_animation(5, 10, "Loading", AnimationType.PROGRESS_BAR)
    assert "Loading [■■■■■□□□□□] 50%" in res


def test_generate_infinite_bar(animation_service):
    res = animation_service._generate_animation(1, 10, "Waiting", AnimationType.INFINITE)
    assert "Waiting [□■□□□□□□□□]" in res


def test_inject_animation_placeholder(animation_service):
    view = UnifiedViewDTO(content=ViewResultDTO(text="Status: {ANIMATION}"))
    res_view = animation_service._inject_animation(view, "[###]")
    assert res_view.content.text == "Status: [###]"


def test_inject_animation_append(animation_service):
    view = UnifiedViewDTO(content=ViewResultDTO(text="Status"))
    res_view = animation_service._inject_animation(view, "[###]")
    assert res_view.content.text == "Status\n\n[###]"


@pytest.mark.asyncio
async def test_run_delayed_fetch(animation_service, mock_sender):
    async def mock_fetch():
        return UnifiedViewDTO(content=ViewResultDTO(text="Done")), False

    # Run with small delay for speed
    await animation_service.run_delayed_fetch(mock_fetch, delay=0.2, step_interval=0.1)

    # Should send at least 2 frames + final result
    assert mock_sender.send.call_count >= 3
    last_call_args = mock_sender.send.call_args[0][0]
    assert last_call_args.content.text == "Done"
