"""
StateHelper — Universal utilities for safe FSMContext data manipulation.

Provides atomic-like operations for getting, updating, and removing keys
from aiogram FSM storage, preventing "zombie dictionaries" in Redis.
"""

from typing import Any

from aiogram.fsm.context import FSMContext


class StateHelper:
    """
    Helper for safe operations with FSMContext data.

    Encapsulates the logic of reading and writing to FSM storage
    to ensure consistency across different modules (StateManager, I18n, etc.).
    """

    @staticmethod
    async def get_value(state: FSMContext, key: str, default: Any = None) -> Any:
        """
        Safely retrieves a value from FSM storage.

        Args:
            state: FSM context.
            key: Storage key.
            default: Default value if key is missing.

        Returns:
            Stored value or default.
        """
        data = await state.get_data()
        return data.get(key, default)

    @staticmethod
    async def update_value(state: FSMContext, key: str, value: Any) -> None:
        """
        Updates a value in FSM storage or removes the key if value is empty.

        If the value is None, an empty dict, or an empty list, the key is
        completely removed from the storage to avoid "zombie" entries in Redis.

        Args:
            state: FSM context.
            key: Storage key.
            value: Value to store.
        """
        data = await state.get_data()

        # Check for "empty" values to trigger deletion
        is_empty = value is None or (isinstance(value, dict | list) and not value)

        if is_empty:
            if key in data:
                del data[key]
                await state.set_data(data)
        else:
            data[key] = value
            await state.set_data(data)

    @staticmethod
    async def clear_key(state: FSMContext, key: str) -> None:
        """
        Completely removes a key from FSM storage.

        Args:
            state: FSM context.
            key: Key to remove.
        """
        await StateHelper.update_value(state, key, None)
