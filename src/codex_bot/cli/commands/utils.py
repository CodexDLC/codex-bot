"""
Developer Connectivity Tools — Telegram ID inspection utilities.

Provides a runtime polling loop to intercept and display User, Chat, and
Channel IDs to facilitate proper routing configuration during development.
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
    """Prints IDs from any private/group message.

    Args:
        message: The incoming message object.
    """
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
    """Prints IDs from channel posts (if bot is admin).

    Args:
        message: The incoming channel post.
    """
    print(f"\n📢 [CHANNEL]  Title: {message.chat.title}")
    print(f"🆔 [CHAT_ID]  {message.chat.id}")
    print("-" * 30)


async def _start_inspector(token: str) -> None:
    """Starts the ID inspection polling loop.

    Args:
        token: Telegram Bot Token.
    """
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
    """Entry point for the inspect command with robust token lookup.

    Args:
        args: Argparse namespace with optional 'token' field.
    """
    token = args.token

    if not token:
        found_envs: list[Path] = []

        # Check current and common parent directories for .env
        paths_to_check = [
            Path.cwd() / ".env",
            Path.cwd().parent / ".env",
            Path.cwd().parent.parent / ".env",
        ]

        for p in paths_to_check:
            if p.exists():
                found_envs.append(p)

        if not found_envs:
            pass  # Handle below
        else:
            if len(found_envs) > 1:
                print("⚠️  Warning: Multiple .env files found:")
                for p in found_envs:
                    print(f"   - {p}")
                print(f"ℹ️  Using the first one: {found_envs[0]}\n")

            from dotenv import load_dotenv

            load_dotenv(dotenv_path=found_envs[0])
            token = os.getenv("BOT_TOKEN")

    if not token or token == "your_bot_token_here":  # nosec B105
        print("\n❌ Error: Telegram Bot Token not found.")
        print(f"Search Path: {Path.cwd()}")
        print("\nPossible solutions:")
        print("  1. Use --token YOUR_TOKEN")
        print("  2. Create a .env file with BOT_TOKEN=...")
        sys.exit(1)

    try:
        asyncio.run(_start_inspector(token))
    except (KeyboardInterrupt, SystemExit):
        print("\n👋 Inspector stopped.")
    except Exception as e:
        print(f"\n🔥 Fatal error: {e}")
        sys.exit(1)
