"""
Default error configuration map for the built-in error feature.

Keys are error type strings sent in Redis ``system_error`` events.
Each entry defines: ``title``, ``text``, ``button_text``, ``action``.

Extend by passing ``custom_errors`` to ``ErrorOrchestrator`` — your entries
win over the defaults on key collision.

Example:
    ```python
    from codex_bot.features.errors import ErrorOrchestrator

    orchestrator = ErrorOrchestrator(
        custom_errors={
            "payment_failed": {
                "title": "Payment Failed",
                "text": "Please try again or contact support.",
                "button_text": "Retry",
                "action": "retry_payment",
            }
        }
    )
    ```
"""

DEFAULT_ERRORS: dict[str, dict[str, str]] = {
    "default": {
        "title": "⚠️ Error",
        "text": "An unexpected error occurred. Please try again later.",
        "button_text": "🔄 Retry",
        "action": "refresh",
    },
    "not_found": {
        "title": "🔍 Not Found",
        "text": "The requested item was not found.",
        "button_text": "🔙 Menu",
        "action": "nav:menu",
    },
    "permission_denied": {
        "title": "⛔ Access Denied",
        "text": "You do not have permission to perform this action.",
        "button_text": "🔙 Back",
        "action": "back",
    },
    "maintenance": {
        "title": "🛠 Maintenance",
        "text": "The bot is under maintenance. We will be back shortly!",
        "button_text": "🔄 Check Again",
        "action": "refresh",
    },
}
