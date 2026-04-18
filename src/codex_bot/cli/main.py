"""
Codex-Bot CLI — The primary toolkit for framework orchestration.

Provides a modular command-line interface for project scaffolding, feature
generation, and database migration management. Uses an extensible sub-command
architecture powered by `argparse`.
"""

from __future__ import annotations

import argparse

from .commands.create_feature import create_feature_command
from .commands.migrations import makemigrations_command, migrate_command

# Import command handlers
from .commands.startproject import start_project_command
from .commands.utils import inspect_ids_command


def main() -> None:
    """Main execution entry for the 'codex-bot' command."""
    parser = argparse.ArgumentParser(
        description="codex-bot: Feature-based Aiogram Bot Management Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # --- Group: Project Creation ---
    sp = subparsers.add_parser("startproject", help="Generate a new bot project")
    sp.add_argument("name", help="Project name (snake_case)")
    sp.add_argument("--mode", choices=["direct", "api"], help="Data mode")
    sp.add_argument("--no-menu", action="store_true", help="Skip bot_menu")
    sp.add_argument("--no-redis", action="store_true", help="Skip Redis")
    sp.add_argument("--i18n", action="store_true", help="Enable i18n")
    sp.add_argument("--loguru", action="store_true", help="Use Loguru")
    sp.add_argument("--force", action="store_true", help="Overwrite existing")
    sp.add_argument("--dev", action="store_true", help="Enable strict development mode (linting, typing)")
    sp.set_defaults(func=start_project_command)

    # --- Group: Feature Management ---
    cf = subparsers.add_parser("create-feature", help="Add a new business module")
    cf.add_argument("name", help="Feature name (snake_case)")
    cf.add_argument("--type", choices=["telegram", "redis"], default="telegram", help="Feature type")
    cf.set_defaults(func=create_feature_command)

    # --- Group: Database (Proxies to Alembic) ---
    mm = subparsers.add_parser("makemigrations", help="Generate a new DB migration")
    mm.add_argument("message", nargs="?", help="Migration comment")
    mm.set_defaults(func=makemigrations_command)

    m = subparsers.add_parser("migrate", help="Apply DB migrations")
    m.add_argument("revision", nargs="?", default="head", help="Target revision")
    m.set_defaults(func=migrate_command)

    # --- Group: Utils ---
    utils = subparsers.add_parser("inspect", help="Tool to find Telegram IDs (User, Chat, Channel)")
    utils.add_argument("--token", help="Telegram Bot Token (if not in .env)")
    utils.set_defaults(func=inspect_ids_command)

    # Parsing and Routing
    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
