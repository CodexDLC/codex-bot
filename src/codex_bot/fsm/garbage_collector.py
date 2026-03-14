"""
Garbage Collector — Automatic cleaning of UI messages.

Tracks FSM states and deletes old UI elements (keyboards/messages)
when a user transitions between scenes or completes a flow.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

from aiogram.filters import Filter
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import TelegramObject

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

log = logging.getLogger(__name__)

# Type alias for objects that can be registered in the GC
RegisterableState = str | State | type[StatesGroup] | Iterable["RegisterableState"]


class GarbageStateRegistry:
    """Registry of FSM states for which the Garbage Collector is active.

    When a user transitions to a state registered here, the system can automatically
    delete messages tracked in the ``_garbage_messages`` FSM data key.

    Example:
        ```python
        GarbageStateRegistry.register(MyStates.input_form)
        GarbageStateRegistry.register([MyStates.step1, MyStates.step2])
        ```
    """

    _states: set[str] = set()

    @classmethod
    def register(cls, state_or_group: RegisterableState) -> None:
        """Adds a state or a group of states to the registry for automatic cleaning.

        Args:
            state_or_group: String state, State object, StatesGroup class, or a collection of these.
        """
        if isinstance(state_or_group, str):
            cls._states.add(state_or_group)
        elif isinstance(state_or_group, State):
            if state_or_group.state:
                cls._states.add(state_or_group.state)
        elif isinstance(state_or_group, type) and issubclass(state_or_group, StatesGroup):
            # In AIogram 3.x, we iterate over class attributes to find States
            for attr_name in dir(state_or_group):
                attr = getattr(state_or_group, attr_name)
                if isinstance(attr, State) and attr.state:
                    cls._states.add(attr.state)
        elif isinstance(state_or_group, list | tuple | set):
            for item in state_or_group:
                cls.register(item)

    @classmethod
    def is_garbage(cls, state: str | None) -> bool:
        """Checks if a state is in the registry.

        Args:
            state: Full state name string (e.g. "MyStates:step1").

        Returns:
            ``True`` if the state is registered for GC.
        """
        return state in cls._states

    @classmethod
    def registered_states(cls) -> frozenset[str]:
        """Returns a read-only view of registered states."""
        return frozenset(cls._states)


class IsGarbageStateFilter(Filter):
    """Aiogram filter to check if the current user state is registered for GC.

    Used by the internal garbage collection middleware/handlers to decide
    when to trigger the cleaning process.
    """

    async def __call__(self, event: TelegramObject, state: FSMContext) -> bool:
        """Checks the current state against the registry.

        Returns:
            ``True`` if current state is in GarbageStateRegistry.
        """
        current_state = await state.get_state()
        return GarbageStateRegistry.is_garbage(current_state)


async def collect_garbage(state: FSMContext, chat_id: int | str, bot: Any) -> None:
    """Performs cleaning of old messages for the current FSM context.

    Iterates through message IDs stored in the ``_garbage_messages`` key of the
    user's FSM data, attempts to delete them from Telegram, and then clears the list.

    Args:
        state: FSM context of the user.
        chat_id: Telegram chat ID.
        bot: Aiogram Bot instance for calling delete_message.
    """
    data = await state.get_data()
    msg_ids = data.get("_garbage_messages", [])

    if not msg_ids:
        return

    for msg_id in msg_ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception as e:
            log.debug(f"GC | Failed to delete message {msg_id}: {e}")

    await state.update_data(_garbage_messages=[])
