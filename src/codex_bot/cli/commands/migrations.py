"""
Database migration commands for codex-bot.
Wraps Alembic functionality for better user experience.
"""

from __future__ import annotations

import subprocess
from argparse import Namespace
from datetime import datetime
from pathlib import Path


def check_alembic_config() -> bool:
    """Checks if alembic.ini exists in the current directory."""
    if not (Path.cwd() / "alembic.ini").exists():
        print("❌ Error: 'alembic.ini' not found. Make sure you are inside your bot package folder.")
        print("Example: cd src/your_bot_name")
        return False
    return True


def makemigrations_command(args: Namespace) -> None:
    """Generates a new migration script using autogenerate."""
    if not check_alembic_config():
        return

    message = args.message
    if not message:
        message = f"auto_{datetime.now().strftime('%Y%m%d_%H%M')}"

    print(f"🚀 Generating migration: {message}...")

    try:
        # Bandit: ignore B603 as we control the input
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)  # nosec B603
        print("✅ Migration generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate migration: {e}")
    except FileNotFoundError:
        print("❌ Error: 'alembic' command not found. Install it via 'pip install alembic'.")


def migrate_command(args: Namespace) -> None:
    """Applies all pending migrations to the database."""
    if not check_alembic_config():
        return

    target = getattr(args, "revision", "head")
    print(f"🚀 Applying migrations to: {target}...")

    try:
        # Bandit: ignore B603 as we control the input
        subprocess.run(["alembic", "upgrade", target], check=True)  # nosec B603
        print("✅ Database is up to date!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
    except FileNotFoundError:
        print("❌ Error: 'alembic' command not found.")
