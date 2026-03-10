"""
codex_bot.engine.middlewares — Ready-to-use middleware for Aiogram.

All middleware are "dumb" bridges between aiogram and the DI container.
No business logic — only infrastructure.

Connection (recommended order):
    1. UserValidationMiddleware  — checks for user presence
    2. ThrottlingMiddleware      — rate limiting (atomic SET NX)
    3. ContainerMiddleware       — DI container injection
"""

from codex_bot.engine.middlewares.container import ContainerMiddleware
from codex_bot.engine.middlewares.throttling import ThrottlingMiddleware
from codex_bot.engine.middlewares.user_validation import UserValidationMiddleware

__all__ = [
    "UserValidationMiddleware",
    "ThrottlingMiddleware",
    "ContainerMiddleware",
]

# FSMContextI18nManager is exported separately — requires aiogram-i18n[optional]
# from codex_bot.engine.middlewares.i18n import FSMContextI18nManager
