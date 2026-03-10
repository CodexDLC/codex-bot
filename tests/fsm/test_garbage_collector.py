import pytest
from aiogram.fsm.state import State, StatesGroup

from codex_bot.fsm.garbage_collector import GarbageStateRegistry


class TestStates(StatesGroup):
    state1 = State()
    state2 = State()


@pytest.fixture(autouse=True)
def clear_registry():
    # Clear registry before each test
    GarbageStateRegistry._states = set()
    yield


def test_register_single_state():
    GarbageStateRegistry.register(TestStates.state1)
    assert GarbageStateRegistry.is_garbage("TestStates:state1") is True
    assert GarbageStateRegistry.is_garbage("TestStates:state2") is False


def test_register_entire_group():
    GarbageStateRegistry.register(TestStates)
    assert GarbageStateRegistry.is_garbage("TestStates:state1") is True
    assert GarbageStateRegistry.is_garbage("TestStates:state2") is True


def test_register_string():
    GarbageStateRegistry.register("custom_state")
    assert GarbageStateRegistry.is_garbage("custom_state") is True


def test_register_list():
    GarbageStateRegistry.register(["state_a", "state_b"])
    assert GarbageStateRegistry.is_garbage("state_a") is True
    assert GarbageStateRegistry.is_garbage("state_b") is True


def test_is_garbage_none():
    assert GarbageStateRegistry.is_garbage(None) is False


def test_registered_states_read_only():
    GarbageStateRegistry.register("state1")
    states = GarbageStateRegistry.registered_states()
    assert "state1" in states
    # states.add("state2")  # This would raise AttributeError because it's a frozenset
