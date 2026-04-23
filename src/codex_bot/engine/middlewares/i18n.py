"""
Localized Storage Manager — Redis-backed I18N orchestration.

Integrates framework-wide internationalization with FSM storage. Manages user
locale preferences using Redis, allowing for efficient, database-agnostic
language resolution without additional I/O overhead.
"""

from typing import Any

from aiogram.fsm.context import FSMContext
from aiogram.types import User

from ...fsm.state_helper import StateHelper

try:
    from aiogram_i18n.managers import BaseManager
except ImportError as e:
    raise ImportError("FSMContextI18nManager requires 'aiogram-i18n'. Install it: pip install codex-bot[i18n]") from e


class FSMContextI18nManager(BaseManager):
    """
    Language manager via FSM storage (Redis).

    Locale determination priority:
    1. FSM storage (key "locale") — user explicitly selected a language.
    2. Telegram language_code — if it's in the allowed_locales list.
    3. default_locale — fallback.

    Args:
        allowed_locales: List of allowed language codes (e.g., ["ru", "en", "de"]).
        default_locale: Default language if nothing matches.

    Example:
        ```python
        from aiogram_i18n import I18nMiddleware
        from aiogram_i18n.cores import FluentRuntimeCore

        i18n = I18nMiddleware(
            core=FluentRuntimeCore(path="locales/{locale}"),
            manager=FSMContextI18nManager(allowed_locales=["ru", "en"], default_locale="en"),
            default_locale="en",
        )
        i18n.setup(dp)
        ```
    """

    def __init__(
        self,
        allowed_locales: list[str] | None = None,
        default_locale: str = "en",
    ) -> None:
        super().__init__(default_locale=default_locale)
        self.allowed_locales: list[str] = allowed_locales or []

    async def get_locale(self, event_from_user: User | None = None, **kwargs: Any) -> str:
        """
        Determines the user's current locale.

        Args:
            event_from_user: Telegram user.
            **kwargs: aiogram-i18n context (includes "state").

        Returns:
            String locale code (e.g., "ru").
        """
        state: FSMContext | None = kwargs.get("state")
        if state:
            locale = await StateHelper.get_value(state, "locale")
            if isinstance(locale, str):
                return locale

        if event_from_user:
            lang = event_from_user.language_code
            if lang and (not self.allowed_locales or lang in self.allowed_locales):
                return lang

        return str(self.default_locale)

    async def set_locale(self, locale: str, **kwargs: Any) -> None:
        """
        Saves the selected locale to FSM.

        Args:
            locale: Language code to save.
            **kwargs: Context (includes "state").
        """
        state: FSMContext | None = kwargs.get("state")
        if state:
            await StateHelper.update_value(state, "locale", locale)
