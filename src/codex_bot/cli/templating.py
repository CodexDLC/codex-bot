"""
Centralized template rendering engine for codex-bot.
Uses Jinja2 for generating project and feature skeletons.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import jinja2


class JinjaRenderer:
    """
    Handles rendering of templates with standard context and filters.
    """

    def __init__(self, templates_dir: Path):
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(templates_dir)),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
            # Security: enable autoescape to pass Bandit checks
            autoescape=jinja2.select_autoescape(["html", "xml", "j2"]),
        )
        # Add custom filters for template convenience
        self.env.filters["pascal"] = self.to_pascal_case
        self.env.filters["python_bool"] = self.to_python_bool

    @staticmethod
    def to_pascal_case(name: str) -> str:
        """Converts snake_case to PascalCase."""
        return "".join(word.capitalize() for word in name.split("_"))

    @staticmethod
    def to_python_bool(val: Any) -> str:
        """Converts value to Python boolean literal string."""
        return "True" if val else "False"

    def render_to_string(self, template_name: str, context: dict[str, Any]) -> str:
        """Renders a template into a string."""
        template = self.env.get_template(template_name)
        return template.render(**context)

    def render_to_file(self, template_name: str, dest_path: Path, context: dict[str, Any]) -> None:
        """Renders a template and writes it to a file, creating directories if needed."""
        content = self.render_to_string(template_name, context)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        dest_path.write_text(content, encoding="utf-8")
