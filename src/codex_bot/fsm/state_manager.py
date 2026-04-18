"""
StateHelper — Atomic abstraction layer for FSM data manipulation.

Provides safe, consistent access to FSM storage for both high-level managers
and low-level infrastructure. Implements aggressive cleanup of empty
structures to optimize backend performance (anti-zombie pattern).
"""

from typing import Any

from aiogram.fsm.context import FSMContext

from .state_helper import StateHelper


class BaseStateManager:
    """Manages namespaced state persistence for individual bot features.

    Each feature is allocated a dedicated sub-key (namespace) within the
    underlying FSM storage (e.g., Redis). This abstraction facilitates
    independent data management and prevents cross-feature state corruption.

    Attributes:
        state: The raw `FSMContext` instance for the current session.
        storage_key: The resolved namespaced key used for persistent storage.
    """

    def __init__(self, state: FSMContext, feature_key: str) -> None:
        """Initializes the BaseStateManager.

        Args:
            state: Instance of `FSMContext` from the active handler.
            feature_key: Unique identifier for the feature (e.g., "market", "quest").
        """
        self.state = state
        self.storage_key = f"draft:{feature_key}"

    async def get_payload(self) -> dict[str, Any]:
        """
        Returns all data of the feature draft.

        Returns:
            Dictionary with current data. Empty dictionary if no data exists.
        """
        result = await StateHelper.get_value(self.state, self.storage_key, {})
        return dict(result) if isinstance(result, dict) else {}

    async def update(self, **kwargs: Any) -> dict[str, Any]:
        """
        Updates the draft with the passed fields (partial update).

        Args:
            **kwargs: Fields to update.

        Returns:
            Updated dictionary with draft data.

        Example:
            ```python
            await manager.update(name="Alice", age=30)
            ```
        """
        current = await self.get_payload()
        current.update(kwargs)
        await StateHelper.update_value(self.state, self.storage_key, current)
        return current

    async def clear(self) -> None:
        """Completely removes the draft key from FSM storage.

        Unlike resetting to ``{key: {}}``, it completely removes the key,
        leaving no empty "zombie dictionaries" in Redis.
        Does not affect data of other features in the same FSM storage.
        """
        await StateHelper.clear_key(self.state, self.storage_key)

    async def set_value(self, key: str, value: Any) -> None:
        """
        Sets one specific value.

        Args:
            key: Field key.
            value: Value to save.
        """
        await self.update(**{key: value})

    async def get_value(self, key: str, default: Any = None) -> Any:
        """
        Returns a specific value from the draft.

        Args:
            key: Field key.
            default: Default value if the key is not found.

        Returns:
            Field value or default.
        """
        payload = await self.get_payload()
        return payload.get(key, default)
