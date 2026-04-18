"""
Internationalization Compiler — Automated Fluent resource orchestration.

Scans the framework's feature directory for localized resources, merging
discrepant `.ftl` files into unified language bundles. Facilitates seamless
integration for `aiogram-i18n` with support for dynamic language resolution.
"""

from __future__ import annotations

import hashlib
import logging
import pathlib
import shutil
import tempfile

log = logging.getLogger(__name__)


def compile_locales(features_path: pathlib.Path) -> str:
    """Discovers and compiles .ftl files from features into an isolated tmp directory.

    Algorithm:
    1. Scans ``features_path`` for any subdirectories named ``locales``.
    2. Inside each ``locales``, finds language folders (e.g., ``ru``, ``en``).
    3. Merges all ``*.ftl`` files for each language into a single ``messages.ftl``.
    4. Places results in ``/tmp/bot_locales_{hash}/{locale}/messages.ftl``.

    Args:
        features_path: Root path to the features directory (e.g. src/my_bot/features).

    Returns:
        Path template string for FluentRuntimeCore: ``"/tmp/bot_locales_{hash}/{locale}"``.
    """
    # 1. Prepare unique isolated directory
    path_hash = hashlib.md5(str(features_path.absolute()).encode(), usedforsecurity=False).hexdigest()[:8]
    tmp_root = pathlib.Path(tempfile.gettempdir()) / f"bot_locales_{path_hash}"

    if tmp_root.exists():
        try:
            shutil.rmtree(tmp_root)
        except OSError as e:
            log.warning(f"LocalesCompiler | Clean failed: {e}")

    tmp_root.mkdir(parents=True, exist_ok=True)

    if not features_path.exists():
        log.error(f"LocalesCompiler | Path not found: {features_path}")
        return str(tmp_root / "{locale}")

    # 2. Discovery and Merging
    # Dictionary structure: { "en": ["content1", "content2"], "ru": [...] }
    merged_data: dict[str, list[str]] = {}

    # Find all 'locales' directories inside features
    for locales_dir in features_path.rglob("locales"):
        if not locales_dir.is_dir():
            continue

        # Look for language subdirectories (ru, en, etc.)
        for lang_dir in locales_dir.iterdir():
            if not lang_dir.is_dir():
                continue

            lang = lang_dir.name
            if lang not in merged_data:
                merged_data[lang] = []

            # Read all FTL files in the language directory
            for ftl_file in sorted(lang_dir.glob("*.ftl")):
                content = ftl_file.read_text(encoding="utf-8")
                # Add source info for easier debugging of translations
                merged_data[lang].append(f"\n### Source: {ftl_file.as_posix()} ###\n{content}")

    # 3. Write results
    for lang, contents in merged_data.items():
        lang_tmp_dir = tmp_root / lang
        lang_tmp_dir.mkdir(parents=True, exist_ok=True)

        output_file = lang_tmp_dir / "messages.ftl"
        output_file.write_text("\n".join(contents), encoding="utf-8")
        log.debug(f"LocalesCompiler | Merged {len(contents)} files for '{lang}' -> {output_file}")

    log.info(f"LocalesCompiler | Compiled {len(merged_data)} languages from {features_path}")
    return str(tmp_root / "{locale}")
