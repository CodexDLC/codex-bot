from unittest.mock import MagicMock

import pytest

from codex_bot.base.base_orchestrator import BaseBotOrchestrator
from codex_bot.base.view_dto import UnifiedViewDTO, ViewResultDTO


class MockOrchestrator(BaseBotOrchestrator[str]):
    async def render_content(self, director: MagicMock, payload: str | None = None) -> ViewResultDTO:
        return ViewResultDTO(text=f"Rendered: {payload}")


@pytest.fixture
def director():
    director = MagicMock()
    director.context_id = 12345
    director.session_key = "user:12345"
    director.trigger_id = None
    return director


@pytest.mark.asyncio
async def test_orchestrator_render_enrichment(director):
    orchestrator = MockOrchestrator()
    payload = "test_payload"

    unified_view = await orchestrator.render(director, payload)

    assert isinstance(unified_view, UnifiedViewDTO)
    assert unified_view.content.text == "Rendered: test_payload"
    assert unified_view.chat_id == 12345
    assert unified_view.session_key == "user:12345"


@pytest.mark.asyncio
async def test_orchestrator_handle_entry_default(director):
    orchestrator = MockOrchestrator()
    payload = "entry_payload"

    # handle_entry by default calls render()
    unified_view = await orchestrator.handle_entry(director, payload)

    assert unified_view.content.text == "Rendered: entry_payload"
    assert unified_view.chat_id == 12345


def test_orchestrator_init_expected_state():
    orchestrator = MockOrchestrator(expected_state="MyState:main")
    assert orchestrator.expected_state == "MyState:main"


def test_orchestrator_init_no_state():
    orchestrator = MockOrchestrator()
    assert orchestrator.expected_state is None
