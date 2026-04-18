from unittest.mock import AsyncMock, MagicMock

import pytest

from codex_bot.base.view_dto import UnifiedViewDTO, ViewResultDTO
from codex_bot.director.director import Director
from codex_bot.director.protocols import OrchestratorProtocol


@pytest.fixture
def director(mock_fsm_context, mock_container):
    return Director(
        container=mock_container,
        state=mock_fsm_context,
        context_id=123,
        session_key=12345,
    )


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
async def test_director_guards_blocking(director, mock_container):
    orchestrator = MagicMock(spec=OrchestratorProtocol)
    mock_container.features = {"feature": orchestrator}

    # Create a blocking guard
    blocking_view = UnifiedViewDTO(alert_text="Access Denied")
    guard = AsyncMock()
    guard.check_access = AsyncMock(return_value=blocking_view)
    mock_container.transition_guards = [guard]

    view = await director.set_scene("feature")

    assert view == blocking_view
    orchestrator.handle_entry.assert_not_called()


@pytest.mark.asyncio
async def test_director_guards_allowing(director, mock_container):
    orchestrator = MagicMock(spec=OrchestratorProtocol)
    orchestrator.handle_entry = AsyncMock(return_value=UnifiedViewDTO(content=ViewResultDTO(text="OK")))
    mock_container.features = {"feature": orchestrator}

    # Create an allowing guard
    guard = AsyncMock()
    guard.check_access = AsyncMock(return_value=True)
    mock_container.transition_guards = [guard]

    view = await director.set_scene("feature")

    assert view.content.text == "OK"
    orchestrator.handle_entry.assert_called_once()


@pytest.mark.asyncio
async def test_director_recursion_prevention_set_scene(director, mock_container):
    orchestrator = MagicMock(spec=OrchestratorProtocol)
    mock_container.features = {"feature": orchestrator}

    # Manually trigger recursion limit
    director._redirect_count = Director.MAX_REDIRECTS
    view = await director.set_scene("feature")

    assert isinstance(view, UnifiedViewDTO)
    assert "цикл" in view.alert_text


@pytest.mark.asyncio
async def test_director_resolve_safe_parsing(director, mock_container):
    orchestrator = MagicMock(spec=OrchestratorProtocol)
    orchestrator.handle_entry = AsyncMock(return_value=UnifiedViewDTO(content=ViewResultDTO(text="Redirected")))
    mock_container.features = {"target": orchestrator}

    # 1. Valid envelope
    data = {"meta": {Director.REDIRECT_KEY: "target"}, "payload": {"key": "value"}}
    view = await director.resolve(data)
    assert view.content.text == "Redirected"
    orchestrator.handle_entry.assert_called_with(director=director, payload={"key": "value"})

    # 2. Redirect not in meta (should not redirect)
    data = {Director.REDIRECT_KEY: "target", "other": "data"}
    result = await director.resolve(data)
    assert result == data  # Returns original dict as payload


@pytest.mark.asyncio
async def test_director_session_enrichment(director, mock_container):
    orchestrator = MagicMock(spec=OrchestratorProtocol)
    orchestrator.handle_entry = AsyncMock(return_value=UnifiedViewDTO(content=ViewResultDTO(text="OK")))
    mock_container.features = {"feature": orchestrator}

    view = await director.set_scene("feature")

    assert view.chat_id == 123
    assert view.session_key == 12345
