"""Generate project structure tree.

This script prefers `codex_core` tooling when present and falls back to a local
implementation otherwise.
"""

from __future__ import annotations

import argparse
from pathlib import Path

try:
    from codex_core.dev.project_tree import ProjectTreeGenerator
except ModuleNotFoundError:  # pragma: no cover - exercised in clean envs
    ProjectTreeGenerator = None  # type: ignore[assignment]


if ProjectTreeGenerator is None:

    class ProjectTreeGenerator:
        """Local project tree generator used without `codex_core`."""

        _SKIP_NAMES = {
            ".git",
            ".venv",
            ".uv-cache",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
            ".idea",
            ".vscode",
        }

        def __init__(self, project_root: Path) -> None:
            self.project_root = project_root.resolve()

        def interactive(self) -> None:
            parser = argparse.ArgumentParser(description="Generate project structure tree.")
            parser.add_argument(
                "--output",
                default="project_structure.txt",
                help="Output file path relative to project root.",
            )
            parser.add_argument(
                "--max-depth",
                type=int,
                default=None,
                help="Limit directory recursion depth.",
            )
            parser.add_argument(
                "--exclude-hidden",
                action="store_true",
                help="Exclude files/directories starting with '.'.",
            )
            args = parser.parse_args()

            output_path = (self.project_root / args.output).resolve()
            lines = [
                "Project Structure: Full Project",
                "===============================",
                "",
                f"📂 {self.project_root.name}/",
            ]
            lines.extend(
                self._build_tree_lines(
                    current=self.project_root,
                    indent="    ",
                    depth=0,
                    max_depth=args.max_depth,
                    exclude_hidden=args.exclude_hidden,
                )
            )
            output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"Saved project tree to: {output_path}")

        def _build_tree_lines(
            self,
            *,
            current: Path,
            indent: str,
            depth: int,
            max_depth: int | None,
            exclude_hidden: bool,
        ) -> list[str]:
            if max_depth is not None and depth > max_depth:
                return []

            try:
                entries = list(current.iterdir())
            except PermissionError:
                return [f"{indent}📄 <permission denied>"]

            def should_keep(path: Path) -> bool:
                if path.name in self._SKIP_NAMES:
                    return False
                return not (exclude_hidden and path.name.startswith("."))

            filtered_entries = [entry for entry in entries if should_keep(entry)]
            filtered_entries.sort(key=lambda item: (item.is_file(), item.name.lower()))

            lines: list[str] = []
            for entry in filtered_entries:
                if entry.is_symlink():
                    continue
                if entry.is_dir():
                    lines.append(f"{indent}📂 {entry.name}/")
                    lines.extend(
                        self._build_tree_lines(
                            current=entry,
                            indent=indent + "    ",
                            depth=depth + 1,
                            max_depth=max_depth,
                            exclude_hidden=exclude_hidden,
                        )
                    )
                else:
                    lines.append(f"{indent}📄 {entry.name}")
            return lines


if __name__ == "__main__":
    ProjectTreeGenerator(Path(__file__).parent.parent.parent).interactive()
