"""
Error UI protocol and default implementation.

``BaseErrorUI`` — structural Protocol (duck typing, no inheritance required).
``DefaultErrorUI`` — renders ``ViewResultDTO`` from a config dict.

The config dict keys:
    title (str): Bold header text.
    text (str): Body text.
    button_text (str): Label of the action button.
    action (str): Callback data for the button (e.g. "refresh", "nav:menu").
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from aiogram.utils.keyboard import InlineKeyboardBuilder

from codex_bot.base.view_dto import ViewResultDTO


@runtime_checkable
class BaseErrorUI(Protocol):
    """Structural protocol for error UI renderers.

    Any class with a matching ``render_error`` signature satisfies this protocol.
    No inheritance needed.

    Example:
        ```python
        class CustomErrorUI:
            def render_error(self, error_config: dict) -> ViewResultDTO:
                return ViewResultDTO(
                    text=f"Custom: {error_config['text']}",
                    kb=None,
                )
        ```
    """

    def render_error(self, error_config: dict[str, str]) -> ViewResultDTO: ...


class DefaultErrorUI:
    """Default error renderer.

    Renders a bold title, body text, and a single action button.

    Args:
        error_config: Dict with keys: ``title``, ``text``, ``button_text``, ``action``.

    Returns:
        ViewResultDTO with HTML-formatted text and inline keyboard.

    Example:
        ```python
        ui = DefaultErrorUI()
        view = ui.render_error({
            "title": "Error",
            "text": "Something went wrong.",
            "button_text": "Retry",
            "action": "refresh",
        })
        ```
    """

    def render_error(self, error_config: dict[str, str]) -> ViewResultDTO:
        title = error_config.get("title", "Error")
        text = error_config.get("text", "An unknown error occurred.")
        button_text = error_config.get("button_text", "OK")
        action = error_config.get("action", "refresh")

        builder = InlineKeyboardBuilder()
        builder.button(text=button_text, callback_data=action)

        return ViewResultDTO(
            text=f"<b>{title}</b>\n\n{text}",
            kb=builder.as_markup(),
        )
