import subprocess
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

# Вычисляем корень проекта (где лежит твой pyproject.toml)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


@pytest.fixture
def mock_fsm_context():
    state = AsyncMock()
    state.get_state = AsyncMock(return_value=None)
    state.set_state = AsyncMock()
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    return state


@pytest.fixture
def mock_redis():
    redis = AsyncMock()
    redis.get = AsyncMock(return_value=None)
    redis.set = AsyncMock()
    return redis


@pytest.fixture
def mock_container():
    container = MagicMock()
    container.features = {}
    container.transition_guards = []
    return container


@pytest.fixture
def sterile_env(tmp_path):
    """
    Creates a sandbox with a clean virtual environment and installs the current library.
    Returns a dictionary with paths to binaries.
    """
    venv_dir = tmp_path / ".venv"

    # 1. Create venv
    print(f"\n[Sandbox] Creating virtual environment in {venv_dir}...")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    # 2. OS-specific binary paths
    if sys.platform == "win32":
        py_bin = venv_dir / "Scripts" / "python.exe"
        cli_bin = venv_dir / "Scripts" / "codex-bot.exe"
    else:
        py_bin = venv_dir / "bin" / "python"
        cli_bin = venv_dir / "bin" / "codex-bot"

    # 3. Install library with dev dependencies [dev] in editable mode
    print("[Sandbox] Installing library and [dev] dependencies (this may take a minute)...")

    # We remove capture_output to let it stream to the console if -s is used
    install_cmd = [str(py_bin), "-m", "pip", "install", "-e", f"{PROJECT_ROOT}[dev]"]

    # We use a simple run without capture to see the progress
    install_res = subprocess.run(install_cmd)

    if install_res.returncode != 0:
        pytest.fail("Failed to install library in venv. Check your internet connection.")

    print("[Sandbox] Setup complete. Running test logic...")
    return {
        "work_dir": tmp_path,
        "python": str(py_bin),
        "cli": str(cli_bin),
    }
