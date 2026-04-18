"""
System Error Feature — Unified Redis-backed error handling.

Provides a comprehensive mechanism for trapping and reporting distributed
system errors via Telegram. Includes built-in support for Redis Stream
event consumption, customizable UI templates, and DI integration.
"""

from .default_errors import DEFAULT_ERRORS
from .orchestrator import ErrorOrchestrator
from .ui import BaseErrorUI, DefaultErrorUI

__all__ = [
    "ErrorOrchestrator",
    "DefaultErrorUI",
    "BaseErrorUI",
    "DEFAULT_ERRORS",
]
