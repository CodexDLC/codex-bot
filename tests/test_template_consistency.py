import ast
from pathlib import Path

from codex_bot.cli.templating import JinjaRenderer

LIB_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = LIB_ROOT / "src" / "codex_bot" / "templates"


def test_template_signature_consistency():
    """
    Ensures that generated orchestrators have signatures matching the base class.
    """
    renderer = JinjaRenderer(TEMPLATES_DIR)
    context = {
        "class_name": "TestFeature",
        "use_loguru": True,
        "project_name": "test_project",
        "bot_class_name": "TestBot",
        "data_mode": "direct",
    }

    templates_to_test = [
        "feature/telegram/logic/orchestrator.py.j2",
        "project/src/features/telegram/bot_menu/logic/orchestrator.py.j2",
    ]

    for t_path in templates_to_test:
        content = renderer.render_to_string(t_path, context)
        tree = ast.parse(content)

        # Verify classes and methods
        found_render_content = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name == "render_content":
                found_render_content = True
                # Check arguments
                args = [arg.arg for arg in node.args.args]
                # Standard signature: self, director, payload
                assert args[:3] == ["self", "director", "payload"], f"Wrong signature in {t_path}: {args}"

        # Some templates might be legacy or special, but core logic ones MUST have it
        if "logic/orchestrator.py.j2" in t_path:
            assert found_render_content, f"render_content not found in {t_path}"
