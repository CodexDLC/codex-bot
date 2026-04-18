import subprocess

import pytest


@pytest.mark.integration
def test_template_generation_quality(sterile_env):
    """
    E2E Test: Generates project, Telegram feature and Redis feature in --dev mode.
    Ensures that all framework-specific features are syntactically correct and type-safe.
    """
    env = sterile_env
    project_dir = env["work_dir"] / "test_bot"
    project_dir.mkdir(parents=True, exist_ok=True)

    # 1. Start Project (Dev mode)
    gen_res = subprocess.run(
        [env["cli"], "startproject", "test_bot", "--mode", "direct", "--loguru", "--force", "--dev"],
        capture_output=True,
        text=True,
        cwd=project_dir,
    )
    assert gen_res.returncode == 0, f"CLI failed during startproject:\n{gen_res.stderr}\n{gen_res.stdout}"

    # 2. Add Telegram Feature
    feature_res = subprocess.run(
        [env["cli"], "create-feature", "my_telegram_feat", "--type", "telegram"],
        capture_output=True,
        text=True,
        cwd=project_dir,
    )
    assert feature_res.returncode == 0, f"CLI failed during telegram feature add:\n{feature_res.stderr}"

    # 3. Add Redis Feature (The framework's unique feature!)
    redis_feature_res = subprocess.run(
        [env["cli"], "create-feature", "my_redis_feat", "--type", "redis"],
        capture_output=True,
        text=True,
        cwd=project_dir,
    )
    assert redis_feature_res.returncode == 0, f"CLI failed during redis feature add:\n{redis_feature_res.stderr}"

    # 4. Type Checking (Mypy) - Strict mode enabled by --dev
    # This will check project core, telegram feature AND redis feature
    mypy_res = subprocess.run([env["python"], "-m", "mypy", "."], capture_output=True, text=True, cwd=project_dir)
    assert mypy_res.returncode == 0, f"Mypy found errors in generated code (--dev mode):\n{mypy_res.stdout}"

    # 5. Linting (Ruff)
    # We run fix first to handle auto-formattable issues (imports, etc.) as suggested by the dev
    subprocess.run(
        [env["python"], "-m", "ruff", "check", "--fix", "."], capture_output=True, text=True, cwd=project_dir
    )

    ruff_res = subprocess.run(
        [env["python"], "-m", "ruff", "check", "."], capture_output=True, text=True, cwd=project_dir
    )
    assert ruff_res.returncode == 0, f"Ruff found errors in generated code (--dev mode):\n{ruff_res.stdout}"

    # 6. Smoke Test: Import verification
    smoke_script = project_dir / "smoke_check.py"
    smoke_script.write_text(
        """
import sys
import os

# Add src to python path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

try:
    from codex_bot.director.director import Director
    from codex_bot.redis.router import RedisRouter

    # Check Director
    d = Director(
        container=None, # type: ignore
        session_key='test_user',
        context_id='test_chat'
    )

    # Check Redis Router (Unique framework component)
    r = RedisRouter()

    print("ALL_GOOD")
except Exception as e:
    import traceback
    print(f"CRASH: {e}")
    traceback.print_exc()
    sys.exit(1)
    """,
        encoding="utf-8",
    )

    smoke_res = subprocess.run([env["python"], str(smoke_script)], capture_output=True, text=True, cwd=project_dir)
    assert smoke_res.returncode == 0, f"Smoke test failed:\n{smoke_res.stdout}\n{smoke_res.stderr}"
    assert "ALL_GOOD" in smoke_res.stdout


@pytest.mark.integration
def test_template_generation_quality_api(sterile_env):
    """
    E2E Test: Generates project in 'api' mode.
    Ensures that Ruff and Mypy pass for this configuration.
    """
    env = sterile_env
    project_dir = env["work_dir"] / "test_bot_api"
    project_dir.mkdir(parents=True, exist_ok=True)

    # 1. Start Project (API mode)
    subprocess.run(
        [env["cli"], "startproject", "test_bot_api", "--mode", "api", "--loguru", "--force", "--dev"],
        capture_output=True,
        text=True,
        cwd=project_dir,
        check=True,
    )

    # 2. Type Checking (Mypy)
    mypy_res = subprocess.run([env["python"], "-m", "mypy", "."], capture_output=True, text=True, cwd=project_dir)
    assert mypy_res.returncode == 0, f"Mypy found errors in API mode:\n{mypy_res.stdout}"

    # 3. Linting (Ruff)
    subprocess.run(
        [env["python"], "-m", "ruff", "check", "--fix", "."], capture_output=True, text=True, cwd=project_dir
    )

    ruff_res = subprocess.run(
        [env["python"], "-m", "ruff", "check", "."], capture_output=True, text=True, cwd=project_dir
    )
    assert ruff_res.returncode == 0, f"Ruff found errors in API mode:\n{ruff_res.stdout}"
