"""
Default Error Schemas — Standard configuration map for system errors.

Provides a foundational set of error templates for common failure modes
(NotFound, AccessDenied, Maintenance). Designed for easy extension via
dictionary merging in the `ErrorOrchestrator`.
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
