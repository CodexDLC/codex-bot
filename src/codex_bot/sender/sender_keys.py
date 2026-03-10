"""
SenderKeys — Key factory for UI coordinate storage.

Used by specific implementations of SenderStateStorageProtocol in projects.
Provided by the library as a ready-made standard for key naming.
"""


class SenderKeys:
    """
    Key factory for SenderManager.

    Standardizes key naming in the UI coordinate storage.
    Use in your implementation of SenderStateStorageProtocol.

    Example:
        ```python
        key = SenderKeys.user(user_id=123456789)
        # "sender:user:123456789"

        key = SenderKeys.channel(session_id="booking_feed_1")
        # "sender:channel:booking_feed_1"
        ```
    """

    @staticmethod
    def user(user_id: int | str) -> str:
        """
        Key for storing UI coordinates of private correspondence.

        Args:
            user_id: Telegram ID of the user.

        Returns:
            Key string like `sender:user:<user_id>`.
        """
        return f"sender:user:{user_id}"

    @staticmethod
    def channel(session_id: str) -> str:
        """
        Key for storing UI coordinates of a channel or group.

        Args:
            session_id: Unique identifier of the channel session.

        Returns:
            Key string like `sender:channel:<session_id>`.
        """
        return f"sender:channel:{session_id}"
