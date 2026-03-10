"""
CLI commands for codex-bot feature scaffolding.

Used as the ``codex-bot`` entry point (see pyproject.toml).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Path to the library's built-in templates
_TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "feature"


def _load_template(name: str, templates_dir: Path) -> str:
    """Loads a template from a ``.py.tpl`` file.

    Args:
        name: Template name without extension.
        templates_dir: Directory containing templates.

    Returns:
        Content of the template file.

    Raises:
        FileNotFoundError: If the template is not found.
    """
    path = templates_dir / f"{name}.py.tpl"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return path.read_text(encoding="utf-8")


def _get_template(base_name: str, suffix: str, templates_dir: Path) -> str:
    """Loads a specific template, otherwise takes the base one.

    Args:
        base_name: Base template name.
        suffix: Suffix for a specific template (e.g., ``"_redis"``).
        templates_dir: Directory containing templates.

    Returns:
        Template content.
    """
    try:
        return _load_template(f"{base_name}{suffix}", templates_dir)
    except FileNotFoundError:
        return _load_template(base_name, templates_dir)


def create_feature(
    name: str,
    feature_type: str,
    base_dir: Path | None = None,
    templates_dir: Path | None = None,
) -> None:
    """Creates the structure of a new feature based on templates.

    Generates a ``features/{feature_type}/{name}/`` directory with files:
    ``feature_setting.py``, ``handlers/handlers.py``, ``logic/orchestrator.py``,
    ``ui/ui.py``, ``contracts/contract.py``, ``resources/``, and ``tests/``.

    Args:
        name: Feature name in ``snake_case``.
        feature_type: Feature type — ``"telegram"`` or ``"redis"``.
        base_dir: Project root directory. ``None`` → current directory.
        templates_dir: Templates directory. ``None`` → built-in templates.

    Raises:
        SystemExit: If the feature already exists or a template is not found.

    Example:
        ```bash
        codex-bot create-feature booking
        codex-bot create-feature payment_notify --type redis
        ```
    """
    base_dir = base_dir or Path.cwd()
    templates_dir = templates_dir or _TEMPLATES_DIR

    feature_base = base_dir / "features" / feature_type / name

    if feature_base.exists():
        print(f"❌ Error: Feature '{name}' already exists in features/{feature_type}/")
        return

    # Name conversions
    class_name = "".join(word.capitalize() for word in name.split("_"))
    feature_key = name.lower()
    container_key = f"redis_{feature_key}" if feature_type == "redis" else feature_key

    # Check for paired feature
    other_type = "redis" if feature_type == "telegram" else "telegram"
    has_pair = (base_dir / "features" / other_type / name).exists()

    # Create directories
    dirs = [
        feature_base,
        feature_base / "handlers",
        feature_base / "logic",
        feature_base / "ui",
        feature_base / "resources",
        feature_base / "contracts",
        feature_base / "tests",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        (d / "__init__.py").write_text("", encoding="utf-8")

    suffix = "_redis" if feature_type == "redis" else ""

    try:
        templates: dict[str, str] = {
            "feature.py": _get_template("feature", suffix, templates_dir),
            "handlers.py": _get_template("handlers", suffix, templates_dir),
            "orchestrator.py": _get_template("orchestrator", suffix, templates_dir),
            "ui.py": _get_template("ui", "", templates_dir),
            "contract.py": _get_template("contract", "", templates_dir),
            "texts.py": _get_template("texts", "", templates_dir),
            "keyboards.py": _get_template("keyboards", "", templates_dir),
            "callbacks.py": _get_template("callbacks", "", templates_dir),
            "formatters.py": _get_template("formatters", "", templates_dir),
            "dto.py": _get_template("dto", "", templates_dir),
        }
    except FileNotFoundError as e:
        print(f"❌ Error: Template file not found. {e}")
        return

    format_vars = {
        "class_name": class_name,
        "feature_key": feature_key,
        "container_key": container_key,
        "feature_type": feature_type,
    }

    files: dict[Path, str] = {
        feature_base / "feature_setting.py": templates["feature.py"],
        feature_base / "handlers" / "handlers.py": templates["handlers.py"],
        feature_base / "logic" / "orchestrator.py": templates["orchestrator.py"],
        feature_base / "ui" / "ui.py": templates["ui.py"],
        feature_base / "contracts" / "contract.py": templates["contract.py"],
        feature_base / "resources" / "texts.py": templates["texts.py"],
        feature_base / "resources" / "keyboards.py": templates["keyboards.py"],
        feature_base / "resources" / "callbacks.py": templates["callbacks.py"],
        feature_base / "resources" / "formatters.py": templates["formatters.py"],
        feature_base / "resources" / "dto.py": templates["dto.py"],
    }

    for file_path, template in files.items():
        content = template.format(**format_vars)
        file_path.write_text(content, encoding="utf-8")

    # Export router from handlers/__init__.py
    router_attr = "redis_router" if feature_type == "redis" else "router"
    init_content = f"from .handlers import {router_attr}\n"
    (feature_base / "handlers" / "__init__.py").write_text(init_content, encoding="utf-8")

    print(f"\n✅ Feature '{name}' ({feature_type}) successfully created!")

    if has_pair:
        print(f"🔗 Paired feature found in '{other_type}'!")
        if feature_type == "telegram":
            print("💡 Tip: Configure inheritance in resources/callbacks.py to handle buttons from Redis notifications.")

    setting_list = "INSTALLED_FEATURES" if feature_type == "telegram" else "INSTALLED_REDIS_FEATURES"
    print(f"👉 Add 'features.{feature_type}.{name}' to {setting_list}")


def main() -> None:
    """CLI entry point for ``codex-bot``.

    Subcommands:
        create-feature: Create a new feature.

    Example:
        ```bash
        codex-bot create-feature booking
        codex-bot create-feature payment_notify --type redis
        ```
    """
    parser = argparse.ArgumentParser(
        description="codex-bot: Aiogram Bot Management Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    create_parser = subparsers.add_parser("create-feature", help="Create a new feature")
    create_parser.add_argument("name", help="Feature name in snake_case")
    create_parser.add_argument(
        "--type",
        choices=["telegram", "redis"],
        default="telegram",
        help="Feature type (default: telegram)",
    )

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if args.command == "create-feature":
        if not args.name:
            create_parser.print_help()
        else:
            create_feature(args.name, args.type)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
