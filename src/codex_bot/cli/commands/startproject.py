"""
Logic for generating a new project skeleton.
Part of the codex-bot CLI.
"""

from __future__ import annotations

import shutil
from argparse import Namespace
from pathlib import Path
from typing import Any

import questionary

from ..templating import JinjaRenderer

# Path to the library's built-in project templates
_LIB_ROOT = Path(__file__).parent.parent.parent
_PROJECT_TEMPLATES = _LIB_ROOT / "templates" / "project"


def interactive_ask(name: str) -> dict[str, Any]:
    """Runs an interactive wizard with conditional branching."""
    print(f"\n🚀 Setting up your new bot: {name}\n")

    answers = questionary.prompt(
        [
            {
                "type": "select",
                "name": "mode",
                "message": "Choose data mode:",
                "choices": [
                    {"name": "Direct (Database via SQLAlchemy)", "value": "direct"},
                    {"name": "API (External backend via HTTP)", "value": "api"},
                ],
            },
            {
                "type": "confirm",
                "name": "use_redis_fsm",
                "message": "Use Redis for FSM (persistent user states)?",
                "default": True,
            },
            {
                "type": "confirm",
                "name": "use_redis_streams",
                "message": "Use Redis Streams (for background events)?",
                "default": False,
                "when": lambda ans: ans.get("use_redis_fsm", False),
            },
            {
                "type": "confirm",
                "name": "use_i18n",
                "message": "Enable internationalization (i18n) support?",
                "default": False,
            },
            {
                "type": "confirm",
                "name": "use_loguru",
                "message": "Use Loguru for professional logging?",
                "default": True,
            },
            {
                "type": "text",
                "name": "bot_token",
                "message": "Enter your Telegram Bot Token (optional):",
                "default": "your_bot_token_here",
            },
            {
                "type": "text",
                "name": "owner_id",
                "message": "Enter Owner Telegram ID (optional):",
                "default": "",
            },
        ]
    )

    if not answers:
        print("❌ Setup cancelled.")
        exit(1)

    if "use_redis_streams" not in answers:
        answers["use_redis_streams"] = False

    return answers


def start_project_command(args: Namespace) -> None:
    """Generates a full project skeleton with isolated package in src/."""
    name: str = args.name
    project_root = Path.cwd()
    package_dir = project_root / "src" / name

    # 1. Safety Check
    critical_files = ["pyproject.toml", "src"]
    if any((project_root / f).exists() for f in critical_files) and not args.force:
        print(f"❌ Error: Directory '{project_root}' already contains a project.")
        return

    # 2. Get Configuration
    is_interactive = args.mode is None
    if is_interactive:
        config = interactive_ask(name)
    else:
        use_redis = not getattr(args, "no_redis", False)
        config = {
            "mode": args.mode,
            "use_redis_fsm": use_redis,
            "use_redis_streams": use_redis,
            "use_i18n": getattr(args, "i18n", False),
            "use_loguru": getattr(args, "loguru", False),
            "bot_token": "your_bot_token_here",
            "owner_id": "",
        }

    renderer = JinjaRenderer(_PROJECT_TEMPLATES)
    any_redis = config["use_redis_fsm"] or config["use_redis_streams"]

    context = {
        "project_name": name,
        "bot_class_name": renderer.to_pascal_case(name),
        "data_mode": config["mode"],
        "use_redis_fsm": config["use_redis_fsm"],
        "use_redis_streams": config["use_redis_streams"],
        "use_redis": any_redis,
        "use_i18n": config["use_i18n"],
        "use_loguru": config["use_loguru"],
        "bot_token": config["bot_token"],
        "owner_id": config["owner_id"],
    }

    # 3. Component Exclusion Rules
    skip_rules = [
        "src/infrastructure/database",
        "root/alembic.ini",
        "root/.env.example",
        "src/app_telegram.py",  # DEPRECATED: now using manage.py + launcher.py
    ]

    if getattr(args, "no_menu", False):
        skip_rules.append("src/features/telegram/bot_menu")
    if not any_redis:
        skip_rules.append("src/infrastructure/redis")
    if not config["use_redis_streams"]:
        skip_rules.append("src/features/redis")
    if not config["use_i18n"]:
        skip_rules.append("src/resources/locales")
    if not config["use_loguru"]:
        skip_rules.append("src/core/logging.py")

    rendered_count = 0
    try:
        for part in ["root", "src"]:
            part_templates_dir = _PROJECT_TEMPLATES / part
            if not part_templates_dir.exists():
                continue

            for src_file in part_templates_dir.rglob("*"):
                if src_file.is_dir():
                    continue

                rel_path = src_file.relative_to(part_templates_dir)
                logical_path = f"{part}/{rel_path.as_posix()}"

                if any(logical_path.startswith(rule) for rule in skip_rules):
                    continue

                dest_path = project_root / rel_path if part == "root" else package_dir / rel_path

                if src_file.suffix == ".j2":
                    final_dest = dest_path.with_suffix("")
                    renderer.render_to_file(logical_path, final_dest, context)
                else:
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest_path)

                rendered_count += 1

    except Exception as e:
        print(f"❌ Error during project generation: {e}")
        return

    # 4. Final Touches
    (package_dir / "tests").mkdir(parents=True, exist_ok=True)
    (project_root / "docs").mkdir(exist_ok=True)
    (package_dir / "__init__.py").touch()
    (package_dir / "tests" / "__init__.py").touch()

    # 5. Output Summary
    print(f"\n✨ Bot Project '{name}' successfully initialized!")
    print(f"📂 Location: {project_root}")

    print("\n🛠  Management Commands:")
    print("  python manage.py run             - Start the bot")
    if config["mode"] == "direct":
        print("  python manage.py makemigrations  - Create DB migration")
        print("  python manage.py migrate         - Apply migrations")

    print("\n🚀 Quick Start:")
    print("  1. pip install -e .")
    print("  2. python manage.py run")
    print("\nHappy coding! 🥂")
