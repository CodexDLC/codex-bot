"""
UIAnimationService — Waiting animation service for Telegram UI.

Three main scenarios: delayed fetch, polling loop, timed polling.
"""

import asyncio
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import TYPE_CHECKING, Any

from codex_bot.base.view_dto import UnifiedViewDTO, ViewResultDTO

if TYPE_CHECKING:
    from codex_bot.sender.view_sender import ViewSender


class AnimationType(Enum):
    """Animation type for displaying progress.

    Attributes:
        PROGRESS_BAR: Fills from 0% to 100%.
        INFINITE: Running indicator (snake).
        NONE: No animation.
    """

    PROGRESS_BAR = "progress_bar"
    INFINITE = "infinite"
    NONE = "none"


PollerFunc = Callable[[], Awaitable[tuple[UnifiedViewDTO, bool]]]
"""Poller function type: returns ``(view, is_waiting)``."""


class UIAnimationService:
    """Service for waiting animation (Polling).

    Three main scenarios:

    - `run_delayed_fetch` — animation for N seconds → one request at the end.
    - `run_polling_loop` — request loop until an event occurs.
    - `run_timed_polling` — immediate request → animation based on duration.

    Args:
        sender: ViewSender instance for sending intermediate frames.

    Example:
        ```python
        animation = UIAnimationService(sender=container.view_sender)

        async def fetch_result() -> tuple[UnifiedViewDTO, bool]:
            data = await api.get_status(user_id)
            return build_view(data), data.is_pending

        await animation.run_polling_loop(
            check_func=fetch_result,
            timeout=60.0,
            loading_text="⏳ <b>Waiting...</b>",
        )
        ```
    """

    def __init__(self, sender: "ViewSender") -> None:
        self.sender = sender

    # =========================================================================
    # Public Methods
    # =========================================================================

    async def run_delayed_fetch(
        self,
        fetch_func: PollerFunc,
        delay: float = 3.0,
        step_interval: float = 1.0,
        loading_text: str = "🔍 <b>Searching...</b>",
        animation_type: AnimationType = AnimationType.PROGRESS_BAR,
    ) -> None:
        """Animation for N seconds → one request at the end.

        Used for: Search, Scan — show animation, then make one request to the backend.

        Args:
            fetch_func: Function to retrieve data (called once at the end).
            delay: Total animation duration in seconds.
            step_interval: Interval between animation frames.
            loading_text: Text to display during animation.
            animation_type: Animation type (PROGRESS_BAR or INFINITE).
        """
        steps = max(1, int(delay / step_interval))

        for i in range(steps):
            anim_str = self._generate_animation(i, steps, loading_text, animation_type)
            temp_view = UnifiedViewDTO(content=ViewResultDTO(text=anim_str))
            await self._send(temp_view)
            await asyncio.sleep(step_interval)

        view_dto, _ = await self._poll_check(fetch_func)
        await self._send(view_dto)

    async def run_polling_loop(
        self,
        check_func: PollerFunc,
        timeout: float = 60.0,
        step_interval: float = 2.0,
        loading_text: str = "⏳ <b>Waiting...</b>",
        animation_type: AnimationType = AnimationType.INFINITE,
    ) -> None:
        """Request loop until an event occurs.

        Used for: Combat polling, Arena waiting — make requests every N seconds
        while ``is_waiting=True``.

        Args:
            check_func: Status check function, returns ``(view, is_waiting)``.
            timeout: Maximum waiting time in seconds.
            step_interval: Interval between checks.
            loading_text: Text to display while waiting.
            animation_type: Animation type (usually INFINITE).
        """
        steps = int(timeout / step_interval)

        for i in range(steps):
            view_dto, is_waiting = await self._poll_check(check_func)

            if is_waiting and view_dto.content:
                anim_str = self._generate_animation(i, steps, loading_text, animation_type)
                view_dto = self._inject_animation(view_dto, anim_str)

            await self._send(view_dto)

            if not is_waiting:
                return

            await asyncio.sleep(step_interval)

    async def run_timed_polling(
        self,
        check_func: PollerFunc,
        duration: float = 5.0,
        step_interval: float = 1.0,
        loading_text: str = "🚶 <b>Moving...</b>",
        animation_type: AnimationType = AnimationType.PROGRESS_BAR,
    ) -> None:
        """Immediate request → animation based on duration from the result.

        Used for: Move — request goes to background immediately, result is stored
        in Redis, show Progress Bar based on time.

        Args:
            check_func: Check function that reads the result from state/Redis.
            duration: Expected animation duration.
            step_interval: Interval between frames.
            loading_text: Text to display.
            animation_type: Animation type (PROGRESS_BAR for timed).
        """
        steps = max(1, int(duration / step_interval))

        for i in range(steps):
            view_dto, is_waiting = await self._poll_check(check_func)

            if not is_waiting:
                await self._send(view_dto)
                return

            anim_str = self._generate_animation(i, steps, loading_text, animation_type)
            view_dto = self._inject_animation(view_dto, anim_str)

            await self._send(view_dto)
            await asyncio.sleep(step_interval)

        # Overflow: Backend slow response → Infinite mode
        infinite_step = 0
        while True:
            view_dto, is_waiting = await self._poll_check(check_func)

            if not is_waiting:
                await self._send(view_dto)
                return

            anim_str = self._generate_animation(infinite_step, steps, loading_text, AnimationType.INFINITE)
            view_dto = self._inject_animation(view_dto, anim_str)

            await self._send(view_dto)
            await asyncio.sleep(step_interval)
            infinite_step += 1

    # =========================================================================
    # Private Helpers
    # =========================================================================

    async def _poll_check(self, func: PollerFunc) -> tuple[UnifiedViewDTO, bool]:
        """Performs status check.

        Args:
            func: Poller function.

        Returns:
            Tuple ``(view, is_waiting)``.
        """
        result: Any = await func()
        if isinstance(result, tuple):
            return result
        return result, False

    def _inject_animation(self, view_dto: UnifiedViewDTO, anim_str: str) -> UnifiedViewDTO:
        """Injects animation string into content, returns new DTO.

        Looks for ``{ANIMATION}`` in text and replaces it, otherwise adds to the end.
        Uses ``model_copy`` since DTO is frozen.

        Args:
            view_dto: Original DTO.
            anim_str: Animation string.

        Returns:
            New ``UnifiedViewDTO`` with updated text.
        """
        if not view_dto.content:
            return view_dto

        original_text = view_dto.content.text
        if "{ANIMATION}" in original_text:
            new_text = original_text.replace("{ANIMATION}", anim_str)
        else:
            new_text = original_text + f"\n\n{anim_str}"

        new_content = view_dto.content.model_copy(update={"text": new_text})
        return view_dto.model_copy(update={"content": new_content})

    async def _send(self, view_dto: UnifiedViewDTO) -> None:
        """Sends View via sender.

        Args:
            view_dto: DTO to send.
        """
        await self.sender.send(view_dto)

    # =========================================================================
    # Animation Generators
    # =========================================================================

    def _generate_animation(
        self,
        step: int,
        total_steps: int,
        text: str,
        animation_type: AnimationType,
    ) -> str:
        """Generates animation string depending on the type.

        Args:
            step: Current step.
            total_steps: Total steps.
            text: Base text.
            animation_type: Animation type.

        Returns:
            String with text and ASCII indicator.
        """
        if animation_type == AnimationType.PROGRESS_BAR:
            return self._gen_progress_bar(step, total_steps, text)
        if animation_type == AnimationType.INFINITE:
            return self._gen_infinite_bar(step, text)
        return text

    def _gen_infinite_bar(self, step: int, text: str) -> str:
        """Running indicator: ``[■□□□□] → [□■□□□] → …``

        Args:
            step: Current step.
            text: Base text.

        Returns:
            String with running indicator.
        """
        total_chars = 10
        position = step % total_chars
        bar = "□" * position + "■" + "□" * (total_chars - position - 1)
        return f"{text} [{bar}]"

    def _gen_progress_bar(self, step: int, total_steps: int, text: str) -> str:
        """Filling indicator: ``[■■□□□] 40%``

        Args:
            step: Current step.
            total_steps: Total steps.
            text: Base text.

        Returns:
            String with progress bar and percentage.
        """
        percent = 1.0 if total_steps == 0 else step / total_steps
        total_chars = 10
        filled = int(total_chars * percent)
        empty = total_chars - filled
        bar = "■" * filled + "□" * empty
        return f"{text} [{bar}] {int(percent * 100)}%"
