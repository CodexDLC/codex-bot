"""
Feature Scaffolding Command — Orchestrates the generation of business modules.

Provides the logic for creating directory structures and rendering templates
for new features, supporting both interactive wizards and CLI arguments.
"""

from __future__ import annotations

import shutil
from argparse import Namespace
from pathlib import Path
from typing import Any

import questionary

from ..templating import JinjaRenderer

# Path to the library's built-in feature templates
_LIB_ROOT = Path(__file__).parent.parent.parent
_FEATURE_TEMPLATES = _LIB_ROOT / "templates" / "feature"


def interactive_ask_feature() -> dict[str, Any]:
    """Runs an interactive wizard for feature creation."""
    print("\n🧩 Creating a new business feature...\n")

    answers = questionary.prompt(
        [
            {
                "type": "select",
                "name": "type",
                "message": "Choose feature type:",
                "choices": [
                    {"name": "Telegram (UI, Handlers, Orchestrator)", "value": "telegram"},
                    {"name": "Redis (Stream Processor, Background tasks)", "value": "redis"},
                ],
            },
            {
                "type": "text",
                "name": "name",
                "message": "Enter feature name (snake_case):",
                "validate": lambda text: len(text) > 0 or "Name cannot be empty",
            },
        ]
    )

    if not answers:
        print("❌ Feature creation cancelled.")
        exit(1)

    return answers


def create_feature_command(args: Namespace) -> None:
    """Creates the structure of a new feature based on templates (.j2).

    Generates a directory tree mirrored from the selected feature type templates.
    Supports both interactive mode and command-line arguments.

    Args:
        args: Argparse namespace.
    """
    # 1. Determine mode (Interactive vs Command-line)
    if args.name is None:
        config = interactive_ask_feature()
        name = config["name"]
        feature_type = config["type"]
    else:
        name = args.name
        feature_type = args.type

    base_dir: Path = Path.cwd()
    feature_base = base_dir / "features" / feature_type / name

    # 2. Validation
    if feature_base.exists():
        print(f"❌ Error: Feature '{name}' already exists in features/{feature_type}/")
        return

    type_templates_dir = _FEATURE_TEMPLATES / feature_type
    if not type_templates_dir.exists():
        print(f"❌ Error: Templates not found for type '{feature_type}'")
        return

    # 3. Prepare Context
    renderer = JinjaRenderer(_FEATURE_TEMPLATES)
    context = {
        "class_name": renderer.to_pascal_case(name),
        "feature_key": name.lower(),
        "feature_type": feature_type,
        "container_key": f"redis_{name.lower()}" if feature_type == "redis" else name.lower(),
    }

    # 4. Rendering
    rendered_files = 0
    try:
        for src in type_templates_dir.rglob("*"):
            if src.is_dir():
                continue

            rel_path = src.relative_to(type_templates_dir)
            dest_path = feature_base / rel_path

            if src.suffix == ".j2":
                dest_path = dest_path.with_suffix("")
                template_name = src.relative_to(_FEATURE_TEMPLATES).as_posix()
                renderer.render_to_file(template_name, dest_path, context)
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest_path)

            rendered_files += 1

    except Exception as e:
        print(f"❌ Critical error during feature generation: {e}")
        if feature_base.exists():
            shutil.rmtree(feature_base)
        return

    # 5. Output Summary
    print(f"\n✨ Feature '{name}' ({feature_type}) successfully created!")
    print(f"📂 Location: {feature_base}")

    setting_list = "INSTALLED_FEATURES" if feature_type == "telegram" else "INSTALLED_REDIS_FEATURES"
    print("\n🛠  Next Step:")
    print(f"  Add 'features.{feature_type}.{name}' to {setting_list} in your settings.")
    print("\nHappy coding! 🥂")
