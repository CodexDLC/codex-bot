"""
LocalesCompiler — Compilation of Fluent (.ftl) locales into a single tmp directory.

Collects all .ftl files from language subfolders and merges them
into one messages.ftl per language for passing to FluentRuntimeCore.

Each project gets an isolated tmp folder based on the hash of the
absolute path to the locales — multiple bots on one server
do not overwrite each other's files.
"""

import hashlib
import logging
import pathlib
import shutil
import tempfile

log = logging.getLogger(__name__)


def compile_locales(base_path: pathlib.Path) -> str:
    """Compiles .ftl files from language subfolders into an isolated tmp directory.

    Collects all ``*.ftl`` files from ``{base_path}/{lang}/*.ftl``
    into ``/tmp/bot_locales_{hash}/{lang}/messages.ftl``.
    The resulting path is passed to ``FluentRuntimeCore``.

    The folder is isolated by the hash of the absolute path: multiple bots or
    parallel tests on the same server do not interfere with each other.

    Args:
        base_path: Path to the directory with language subfolders.

    Returns:
        Path template ``"/tmp/bot_locales_{hash}/{locale}"`` for ``FluentRuntimeCore``.

    Raises:
        OSError: If the tmp directory cannot be created or files cannot be written.

    Example:
        ```python
        from codex_bot.engine.i18n import compile_locales

        locales_path = compile_locales(Path("resources/locales"))
        core = FluentRuntimeCore(path=locales_path)
        ```
    """
    # Short hash of the absolute path — unique per project, stable between restarts
    # usedforsecurity=False tells Bandit/linters that this is not a cryptographic hash.
    path_hash = hashlib.md5(str(base_path.absolute()).encode(), usedforsecurity=False).hexdigest()[:8]
    tmp_dir = pathlib.Path(tempfile.gettempdir()) / f"bot_locales_{path_hash}"

    if tmp_dir.exists():
        try:
            shutil.rmtree(tmp_dir)
        except OSError as e:
            log.warning(f"LocalesCompiler | Failed to clean tmp_dir (maybe in use): {e}")

    tmp_dir.mkdir(parents=True, exist_ok=True)

    if not base_path.exists():
        log.warning(f"LocalesCompiler | Source path not found: {base_path}")
        return str(tmp_dir / "{locale}")

    for lang_dir in base_path.iterdir():
        if not lang_dir.is_dir():
            continue

        lang = lang_dir.name
        compiled_content: list[str] = []

        for ftl_file in sorted(lang_dir.glob("*.ftl")):
            content = ftl_file.read_text(encoding="utf-8")
            compiled_content.append(f"### Source: {ftl_file.name} ###\n{content}\n")

        if compiled_content:
            lang_tmp_dir = tmp_dir / lang
            lang_tmp_dir.mkdir(exist_ok=True)
            output_file = lang_tmp_dir / "messages.ftl"
            output_file.write_text("\n".join(compiled_content), encoding="utf-8")
            log.debug(f"LocalesCompiler | Compiled {lang} ({len(compiled_content)} files) → {output_file}")

    return str(tmp_dir / "{locale}")
