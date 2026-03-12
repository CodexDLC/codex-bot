"""
Automated "Zero-Maintenance" tests for all Jinja2 templates.
Walks through the entire templates directory and renders everything.
"""

from pathlib import Path

import pytest

from codex_bot.cli.templating import JinjaRenderer

# Global templates root
LIB_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = LIB_ROOT / "src" / "codex_bot" / "templates"


def get_all_template_paths():
    """Discovers every single .j2 file in the library."""
    return [p.relative_to(TEMPLATES_DIR).as_posix() for p in TEMPLATES_DIR.rglob("*.j2")]


# Test contexts to cover different branches (if/else)
TEST_CONTEXTS = [
    # 1. Full feature set (direct mode)
    {
        "project_name": "full_bot",
        "bot_class_name": "FullBot",
        "data_mode": "direct",
        "use_redis_fsm": True,
        "use_redis_streams": True,
        "use_redis": True,
        "use_i18n": True,
        "use_loguru": True,
        "bot_token": "123:abc",
        "owner_id": "12345",
        "lib_version": "0.2.0",
        "timestamp": "2024-03-12",
        "feature_key": "test_feature",
        "class_name": "TestFeature",
    },
    # 2. Minimal set (api mode, no redis, no i18n)
    {
        "project_name": "mini_bot",
        "bot_class_name": "MiniBot",
        "data_mode": "api",
        "use_redis_fsm": False,
        "use_redis_streams": False,
        "use_redis": False,
        "use_i18n": False,
        "use_loguru": False,
        "bot_token": "123:abc",
        "owner_id": "",
        "lib_version": "0.2.0",
        "timestamp": "2024-03-12",
        "feature_key": "test_feature",
        "class_name": "TestFeature",
    },
]


@pytest.mark.parametrize("template_rel_path", get_all_template_paths())
@pytest.mark.parametrize("context", TEST_CONTEXTS)
def test_render_all_templates(template_rel_path: str, context: dict):
    """
    Automatic test for every template file found in the library.
    Ensures syntax validity and variable resolution.
    """
    # Initialize renderer from the global templates root
    renderer = JinjaRenderer(TEMPLATES_DIR)

    try:
        # Attempt to render
        result = renderer.render_to_string(template_rel_path, context)

        # Basic sanity check: result should not be empty if template isn't empty
        template_content = (TEMPLATES_DIR / template_rel_path).read_text(encoding="utf-8").strip()
        if template_content:
            assert result.strip() != "", f"Template {template_rel_path} rendered to an empty string"

    except Exception as e:
        pytest.fail(f"🚨 Template Syntax Error in '{template_rel_path}' with context {context['project_name']}:\n{e}")
