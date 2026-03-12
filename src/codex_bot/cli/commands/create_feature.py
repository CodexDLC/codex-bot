"""
Logic for generating a new feature structure.
Part of the codex-bot CLI.
"""

from __future__ import annotations

import shutil
from argparse import Namespace
from pathlib import Path

from ..templating import JinjaRenderer

# Path to the library's built-in feature templates
_LIB_ROOT = Path(__file__).parent.parent.parent
_FEATURE_TEMPLATES = _LIB_ROOT / "templates" / "feature"


def create_feature_command(args: Namespace) -> None:
    """Creates the structure of a new feature based on templates (.j2).

    Generates a directory tree mirrored from the selected feature type templates.
    By default, it creates files like: ``feature_setting.py``, ``handlers/handlers.py``,
    ``logic/orchestrator.py``, ``ui/ui.py``, etc.

    Supports atomic creation: if any step fails, the partially created feature
    directory is automatically removed to prevent garbage.

    Args:
        args: Argparse namespace containing:
            name: Feature name in ``snake_case``.
            type: Feature type — ``"telegram"`` or ``"redis"``.

    Example:
        ```bash
        codex-bot create-feature booking
        codex-bot create-feature payment_notify --type redis
        ```
    """
    name: str = args.name
    feature_type: str = args.type
    base_dir: Path = Path.cwd()

    feature_base = base_dir / "features" / feature_type / name

    if feature_base.exists():
        print(f"❌ Error: Feature '{name}' already exists in features/{feature_type}/")
        return

    # Find the source folder for the specific feature type (telegram/redis)
    type_templates_dir = _FEATURE_TEMPLATES / feature_type
    if not type_templates_dir.exists():
        print(f"❌ Error: Templates not found for type '{feature_type}' in {type_templates_dir}")
        return

    # Prepare context
    renderer = JinjaRenderer(_FEATURE_TEMPLATES)
    context = {
        "class_name": renderer.to_pascal_case(name),
        "feature_key": name.lower(),
        "feature_type": feature_type,
        "container_key": f"redis_{name.lower()}" if feature_type == "redis" else name.lower(),
    }

    rendered_files = 0
    try:
        # Dynamic traversal of all files in the source template directory
        for src in type_templates_dir.rglob("*"):
            if src.is_dir():
                continue

            # Calculate the destination path relative to the feature base
            rel_path = src.relative_to(type_templates_dir)
            dest_path = feature_base / rel_path

            if src.suffix == ".j2":
                # Cleanly remove .j2 extension for the final filename
                dest_path = dest_path.with_suffix("")

                # Jinja needs the path relative to the loader root (_FEATURE_TEMPLATES)
                template_name = src.relative_to(_FEATURE_TEMPLATES).as_posix()
                renderer.render_to_file(template_name, dest_path, context)
            else:
                # Direct copy for non-template files (e.g. __init__.py, assets)
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest_path)

            rendered_files += 1

    except Exception as e:
        # Atomic rollback: remove broken files on error
        print(f"❌ Critical error during feature generation: {e}")
        print("🧹 Performing cleanup (removing incomplete feature directory)...")
        if feature_base.exists():
            shutil.rmtree(feature_base)
        return

    print(f"\n✅ Feature '{name}' ({feature_type}) successfully created! (Files: {rendered_files})")

    # Paired feature detection
    paired_type = "redis" if feature_type == "telegram" else "telegram"
    if (base_dir / "features" / paired_type / name).exists():
        print(f"🔗 Paired {paired_type} feature found!")

    setting_list = "INSTALLED_FEATURES" if feature_type == "telegram" else "INSTALLED_REDIS_FEATURES"
    print(f"👉 Add 'features.{feature_type}.{name}' to {setting_list}")
