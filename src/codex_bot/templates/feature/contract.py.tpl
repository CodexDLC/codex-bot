from typing import Any, Protocol


class {class_name}DataProvider(Protocol):
    """
    Contract for accessing {class_name} feature data.
    Implementation (Client or Repository) is injected via DI.
    """

    async def get_data(self, user_id: int) -> Any:
        """Example data retrieval method."""
        ...
