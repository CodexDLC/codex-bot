"""
Database Migration Commands — Administrative proxies for Alembic.

Provides a unified interface for generating and applying schema migrations.
Encapsulates environment validation and command execution logic to ensure
consistent database evolution across projects.
"""

from __future__ import annotations

import shutil
import subprocess
from argparse import Namespace
from datetime import datetime
from pathlib import Path


def check_alembic_availability() -> bool:
    """Checks if the 'alembic' command is available in the system.

    Returns:
        True if alembic is found, False otherwise.
    """
    if shutil.which("alembic") is None:
        print("❌ Error: 'alembic' command not found.")
        print("Please install it via: pip install alembic")
        return False
    return True


def check_alembic_config() -> bool:
    """Checks if alembic.ini exists in the current directory.

    Returns:
        True if config exists, False otherwise.
    """
    if not (Path.cwd() / "alembic.ini").exists():
        print("❌ Error: 'alembic.ini' not found.")
        print("Make sure you are inside your bot package folder (e.g. src/my_bot/).")
        return False
    return True


def makemigrations_command(args: Namespace) -> None:
    """Generates a new migration script using autogenerate.

    Args:
        args: Argparse namespace with 'message' field.
    """
    if not check_alembic_availability() or not check_alembic_config():
        return

    message = args.message
    if not message:
        message = f"auto_{datetime.now().strftime('%Y%m%d_%H%M')}"

    print(f"🚀 Generating migration: {message}...")

    try:
        subprocess.run(["alembic", "revision", "--autogenerate", "-m", message], check=True)  # nosec B603
        print("✅ Migration generated successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate migration: {e}")


def migrate_command(args: Namespace) -> None:
    """Applies all pending migrations to the database.

    Args:
        args: Argparse namespace with 'revision' field.
    """
    if not check_alembic_availability() or not check_alembic_config():
        return

    target = getattr(args, "revision", "head")
    print(f"🚀 Applying migrations to: {target}...")

    try:
        subprocess.run(["alembic", "upgrade", target], check=True)  # nosec B603
        print("✅ Database is up to date!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Migration failed: {e}")
