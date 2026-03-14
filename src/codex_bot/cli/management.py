"""
Management Utility — Project-level administrative orchestrator.

This module provides the logic for the `manage.py` script included in every
bot project. It encapsulates operational tasks such as application launching
and database migration proxying, ensuring the project's entry point remains
minimal.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def execute_from_command_line(argv: list[str] | None = None) -> None:
    """Parses and executes management commands for a codex-bot project."""
    argv = argv or sys.argv
    project_name = os.environ.get("CODEX_BOT_PROJECT")

    if not project_name:
        print("❌ Error: CODEX_BOT_PROJECT environment variable is not set.")
        sys.exit(1)

    parser = argparse.ArgumentParser(description=f"Management Tool for {project_name}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Command: run
    subparsers.add_parser("run", help="Start the Telegram bot")

    # 2. Command: makemigrations
    mm_parser = subparsers.add_parser("makemigrations", help="Create a new DB migration")
    mm_parser.add_argument("message", nargs="?", help="Migration comment")

    # 3. Command: migrate
    m_parser = subparsers.add_parser("migrate", help="Apply migrations to DB")
    m_parser.add_argument("revision", nargs="?", default="head", help="Revision to upgrade to")

    args = parser.parse_args(argv[1:])

    # Command Execution Logic
    if args.command == "run":
        _run_app(project_name)
    elif args.command == "makemigrations":
        _makemigrations(project_name, args.message)
    elif args.command == "migrate":
        _migrate(project_name, args.revision)


def _setup_python_path() -> None:
    """Adds 'src' directory to sys.path to make the project package discoverable."""
    src_path = Path.cwd() / "src"
    if src_path.exists() and str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))


def _run_app(project_name: str) -> None:
    """Imports and runs the bot's launcher."""
    _setup_python_path()
    try:
        # Dynamic import of the project's launcher
        import importlib

        launcher = importlib.import_module(f"{project_name}.launcher")
        launcher.run()
    except ImportError as e:
        print(f"❌ Error: Could not import '{project_name}.launcher'.")
        print(f"Details: {e}")
        sys.exit(1)


def _makemigrations(project_name: str, message: str | None) -> None:
    """Proxies the makemigrations command to Alembic."""
    config_path = Path("src") / project_name / "alembic.ini"
    if not config_path.exists():
        print(f"❌ Error: alembic.ini not found at {config_path}")
        return

    cmd = ["alembic", "-c", str(config_path), "revision", "--autogenerate"]
    if message:
        cmd.extend(["-m", message])

    try:
        subprocess.run(cmd, check=True)  # nosec B603
    except subprocess.CalledProcessError:
        sys.exit(1)


def _migrate(project_name: str, revision: str) -> None:
    """Proxies the migrate command to Alembic."""
    config_path = Path("src") / project_name / "alembic.ini"
    if not config_path.exists():
        print(f"❌ Error: alembic.ini not found at {config_path}")
        return

    cmd = ["alembic", "-c", str(config_path), "upgrade", revision]
    try:
        subprocess.run(cmd, check=True)  # nosec B603
    except subprocess.CalledProcessError:
        sys.exit(1)
