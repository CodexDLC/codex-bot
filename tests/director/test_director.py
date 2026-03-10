from unittest.mock import AsyncMock, MagicMock

import pytest

from codex_bot.base.view_dto import UnifiedViewDTO, ViewResultDTO
from codex_bot.director.director import Director
from codex_bot.director.protocols import OrchestratorProtocol


@pytest.fixture
def director(mock_fsm_context, mock_container):
    return Director(container=mock_container, state=mock_fsm_context, chat_id=123, user_id=12345)


@pytest.mark.asyncio
async def test_director_set_scene_success(director, mock_fsm_context, mock_container):
    # Create a mock that implements OrchestratorProtocol
    orchestrator = MagicMock(spec=OrchestratorProtocol)
    orchestrator.expected_state = "NewState:main"

    # Both methods must be AsyncMock
    orchestrator.handle_entry = AsyncMock(return_value=UnifiedViewDTO(content=ViewResultDTO(text="OK")))
    orchestrator.render = AsyncMock(return_value=UnifiedViewDTO(content=ViewResultDTO(text="OK")))

    mock_container.features = {"test_feature": orchestrator}

    view = await director.set_scene("test_feature")

    # Check if state was changed
    mock_fsm_context.set_state.assert_called_once_with("NewState:main")
    # Check if handle_entry was called
    orchestrator.handle_entry.assert_called_once_with(director=director, payload=None)
    assert view.content.text == "OK"


@pytest.mark.asyncio
async def test_director_set_scene_not_found(director, mock_container):
    mock_container.features = {}
    view = await director.set_scene("unknown")
    assert view is None


@pytest.mark.asyncio
async def test_director_get_state(director, mock_fsm_context):
    mock_fsm_context.get_state = AsyncMock(return_value="current_state")
    state = await director.state.get_state()
    assert state == "current_state"


@pytest.mark.asyncio
async def test_director_update_data(director, mock_fsm_context):
    mock_fsm_context.update_data = AsyncMock()
    await director.state.update_data(a=1, b=2)
    mock_fsm_context.update_data.assert_called_once_with(a=1, b=2)
