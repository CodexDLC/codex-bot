"""
GarbageStateRegistry and IsGarbageStateFilter — Automatic deletion
of text messages in states where only button clicks are expected.

The registry is filled dynamically when features are loaded via
FeatureDiscoveryService or directly via GarbageStateRegistry.register().
This allows any feature to declare its states as "garbage" without
touching the global configuration.

Example:
    ```python
    # In feature_setting.py of a feature:
    from aiogram.fsm.state import State, StatesGroup

    class BookingStates(StatesGroup):
        select_date = State()
        select_time = State()

    # Register the entire group as garbage:
    GarbageStateRegistry.register(BookingStates)

    # Or a single state:
    GarbageStateRegistry.register(BookingStates.select_date)
    ```
"""

from typing import Any

from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message


class GarbageStateRegistry:
    """
    Registry of FSM states where text messages are considered garbage.

    Global registry: states are registered once at startup,
    the filter checks the user's current state with each message.

    Supports registration of:
    - a single `State` object
    - an entire `StatesGroup` (all states in the group)
    - a string (state name)
    - a list / tuple / set of the above types

    Example:
        ```python
        GarbageStateRegistry.register(MyFeatureStates)          # entire group
        GarbageStateRegistry.register(MyFeatureStates.waiting)  # single state
        GarbageStateRegistry.register(["Feature1:main", "Feature2:step1"])
        ```
    """

    _states: set[str] = set()

    @classmethod
    def register(
        cls,
        state: State | StatesGroup | type[StatesGroup] | str | list[Any] | tuple[Any, ...] | set[Any],
    ) -> None:
        """
        Registers state(s) as garbage.

        Args:
            state: State, StatesGroup, string, or an iterable of them.
        """
        if isinstance(state, list | tuple | set):
            for s in state:
                cls.register(s)
            return

        # StatesGroup class (not instance) — take all its states
        if isinstance(state, type) and issubclass(state, StatesGroup):
            for s in state.__all_states__:
                cls.register(s)
            return

        # StatesGroup instance — take __all_states__ (Aiogram 3)
        if hasattr(state, "__all_states__"):
            for s in state.__all_states__:
                cls.register(s)
            return

        # State object or string
        state_name = state.state if isinstance(state, State) else str(state)
        if state_name:
            cls._states.add(state_name)

    @classmethod
    def is_garbage(cls, state_name: str | None) -> bool:
        """
        Checks if a state is registered as garbage.

        Args:
            state_name: String name of the current FSM state.

        Returns:
            True if the state is registered as garbage.
        """
        if state_name is None:
            return False
        return state_name in cls._states

    @classmethod
    def registered_states(cls) -> frozenset[str]:
        """
        Returns all registered garbage states (read-only).

        Returns:
            Frozenset of string state names.
        """
        return frozenset(cls._states)


class IsGarbageStateFilter(Filter):
    """
    Aiogram filter: True if the user's current FSM state is garbage.

    Used in common_fsm_router for automatic deletion of unwanted text messages.

    Example:
        ```python
        @router.message(F.text, IsGarbageStateFilter())
        async def delete_garbage(message: Message, state: FSMContext):
            await message.delete()
        ```
    """

    async def __call__(self, message: Message, state: FSMContext) -> bool:
        """
        Args:
            message: Incoming message.
            state: User's FSM context.

        Returns:
            True if the current state is registered as garbage.
        """
        current_state = await state.get_state()
        return GarbageStateRegistry.is_garbage(current_state)
