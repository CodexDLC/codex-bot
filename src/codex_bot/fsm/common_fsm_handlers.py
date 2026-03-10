"""
common_fsm_router — Common FSM handlers for the entire bot.

Connected to the main router via build_main_router() or manually:
    dp.include_router(common_fsm_router)

Current set of handlers:
    - Garbage Collector: deletes text messages in "garbage" states.
"""

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .garbage_collector import IsGarbageStateFilter

log = logging.getLogger(__name__)

common_fsm_router = Router(name="codex_bot:common_fsm_router")


@common_fsm_router.message(F.text, IsGarbageStateFilter())
async def delete_garbage_text(message: Message, state: FSMContext) -> None:
    """
    Deletes unwanted text messages in "garbage" states.

    Triggers only if the user's current FSM state is registered
    in GarbageStateRegistry. States are added dynamically as features load.

    Args:
        message: Incoming text message.
        state: User's FSM context.
    """
    user_id = message.from_user.id if message.from_user else "N/A"
    current_state = await state.get_state()
    log.info(f"GarbageCollector | user={user_id} state={current_state}")

    try:
        await message.delete()
        text_preview = (message.text or "")[:20]
        log.debug(f"GarbageCollector | status=deleted user={user_id} text='{text_preview}'")
    except TelegramAPIError as e:
        log.warning(f"GarbageCollector | status=delete_failed user={user_id} error='{e}'")
