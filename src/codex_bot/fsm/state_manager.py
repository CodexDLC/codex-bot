"""
BaseStateManager — Isolated feature data storage within FSM.

Each feature works with its own namespaced key in the FSM storage,
eliminating conflicts between features of the same bot.
"""

from typing import Any, TypeVar

from aiogram.fsm.context import FSMContext

from .state_helper import StateHelper

T = TypeVar("T")


class BaseStateManager:
    """
    Base FSM state manager for a feature (draft).

    Isolates specific feature data under the `draft:<feature_key>` key
    within the user's general FSM storage. This prevents collisions
    between different features operating in the same FSM session.

    Args:
        state: FSM context of the current user.
        feature_key: Unique feature key (e.g., `"booking"`, `"profile"`).

    Example:
        ```python
        manager = BaseStateManager(state, feature_key="booking")
        await manager.update(date="2024-01-15", time="14:00")
        payload = await manager.get_payload()
        # {"date": "2024-01-15", "time": "14:00"}
        await manager.clear()
        ```
    """

    def __init__(self, state: FSMContext, feature_key: str) -> None:
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
