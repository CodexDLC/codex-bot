import pytest

from codex_bot.fsm.state_manager import BaseStateManager


@pytest.fixture
def state_manager(mock_fsm_context):
    return BaseStateManager(mock_fsm_context, feature_key="test_feature")


@pytest.mark.asyncio
async def test_state_manager_update(state_manager, mock_fsm_context):
    mock_fsm_context.get_data.return_value = {}

    await state_manager.update(key="val")

    # Check if set_data was called with nested dict (StateHelper uses set_data)
    mock_fsm_context.set_data.assert_called_once_with({"draft:test_feature": {"key": "val"}})


@pytest.mark.asyncio
async def test_state_manager_get_payload(state_manager, mock_fsm_context):
    mock_fsm_context.get_data.return_value = {"draft:test_feature": {"a": 1}}

    payload = await state_manager.get_payload()
    assert payload == {"a": 1}


@pytest.mark.asyncio
async def test_state_manager_clear(state_manager, mock_fsm_context):
    mock_fsm_context.get_data.return_value = {"draft:test_feature": {"a": 1}, "other": 2}

    await state_manager.clear()

    # Should call set_data without the feature key
    mock_fsm_context.set_data.assert_called_once_with({"other": 2})


@pytest.mark.asyncio
async def test_state_manager_set_get_value(state_manager, mock_fsm_context):
    mock_fsm_context.get_data.return_value = {"draft:test_feature": {"my_key": "res"}}

    val = await state_manager.get_value("my_key")
    assert val == "res"

    await state_manager.set_value("new_key", "new_val")
    # set_data should be called with merged dict
    mock_fsm_context.set_data.assert_called_once()
