"""
Developer utilities for codex-bot.
Provides tools for inspecting Telegram IDs and other debug tasks.
"""

from __future__ import annotations

import asyncio
import os
import sys
from argparse import Namespace
from pathlib import Path

from aiogram import Bot, Dispatcher, Router, types
from aiogram.exceptions import TelegramConflictError

# Pre-define router for events
router = Router()


@router.message()
async def handle_any_message(message: types.Message) -> None:
    """Prints IDs from any private/group message."""
    if not message.from_user:
        return

    print(f"\n👤 [USER]     Name: {message.from_user.full_name} (@{message.from_user.username})")
    print(f"🆔 [USER_ID]  {message.from_user.id}")
    print(f"💬 [CHAT]     Type: {message.chat.type} | Title: {message.chat.title or 'N/A'}")
    print(f"🆔 [CHAT_ID]  {message.chat.id}")
    if message.message_thread_id:
        print(f"🧵 [THREAD_ID] {message.message_thread_id}")
    print("-" * 30)


@router.channel_post()
async def handle_channel_post(message: types.Message) -> None:
    """Prints IDs from channel posts (if bot is admin)."""
    print(f"\n📢 [CHANNEL]  Title: {message.chat.title}")
    print(f"🆔 [CHAT_ID]  {message.chat.id}")
    print("-" * 30)


async def _start_inspector(token: str) -> None:
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    print("\n🚀 ID Inspector started!")
    print("👉 Send any message to your bot to see IDs.")
    print("⌨️  Press Ctrl+C to stop.\n")

    try:
        await dp.start_polling(bot)
    except TelegramConflictError:
        print("\n⚠️  CONFLICT DETECTED!")
        print("Another instance of this bot is already running (check Docker or other terminals).")
        print("Please stop the other instance and try again.")
    except Exception as e:
        print(f"\n🔥 Error during polling: {e}")
    finally:
        await bot.session.close()


def inspect_ids_command(args: Namespace) -> None:
    """Entry point for the inspect command with robust token lookup."""
    token = args.token

    if not token:
        # 1. Try to load from current directory
        env_path = Path.cwd() / ".env"
        if env_path.exists():
            from dotenv import load_dotenv

            load_dotenv(dotenv_path=env_path)
            token = os.getenv("BOT_TOKEN")
            if token:
                print(f"ℹ️  Token loaded from: {env_path}")
        else:
            # 2. Try common package structure
            parent_env = Path.cwd().parent.parent / ".env"
            if parent_env.exists():
                from dotenv import load_dotenv

                load_dotenv(dotenv_path=parent_env)
                token = os.getenv("BOT_TOKEN")
                if token:
                    print(f"ℹ️  Token loaded from parent: {parent_env}")

    # Bandit: ignore B105 as this is a placeholder string
    if not token or token == "your_bot_token_here":  # nosec B105
        print("\n❌ Error: Telegram Bot Token not found.")
        print(f"Current Path: {Path.cwd()}")
        print("\nPossible solutions:")
        print("  1. Use --token YOUR_TOKEN")
        print("  2. Create a .env file with BOT_TOKEN=...")
        print("  3. Run this command from the project root folder.")
        sys.exit(1)

    try:
        asyncio.run(_start_inspector(token))
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Inspector stopped.")
    except Exception as e:
        print(f"\n🔥 Fatal error: {e}")
        sys.exit(1)
