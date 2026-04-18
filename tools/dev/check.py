"""Quality gate for codex-bot.

This script prefers shared `codex_core` tooling when available, but keeps a
local fallback runner so the repository stays self-validating in clean setups.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    from codex_core.dev.check_runner import BaseCheckRunner
except ModuleNotFoundError:  # pragma: no cover - exercised in clean envs
    BaseCheckRunner = None  # type: ignore[assignment]


if BaseCheckRunner is not None:

    class CheckRunner(BaseCheckRunner):
        """Thin launcher; project policy lives in pyproject.toml."""


else:

    @dataclass(frozen=True)
    class CheckStep:
        """Single quality gate command."""

        name: str
        command: list[str]

    class CheckRunner:
        """Local self-contained runner used when `codex_core` is unavailable."""

        PROJECT_NAME = "codex-bot"
        INTEGRATION_REQUIRES = "Redis"

        def __init__(self, project_root: Path) -> None:
            self.project_root = project_root.resolve()

        def main(self) -> None:
            args = self._parse_args()
            steps = self._build_steps(args)

            print(f"[check] Running quality gate for {self.PROJECT_NAME} in {self.project_root}")
            failed_steps: list[str] = []

            for step in steps:
                print(f"\n[check] {step.name}")
                print(f"[check] > {' '.join(step.command)}")
                result = subprocess.run(step.command, cwd=self.project_root, check=False)  # nosec B603
                if result.returncode != 0:
                    failed_steps.append(step.name)
                    print(f"[check] FAIL: {step.name} (exit {result.returncode})")
                    if args.fail_fast:
                        break
                else:
                    print(f"[check] OK: {step.name}")

            if failed_steps:
                print("\n[check] Failed steps:")
                for name in failed_steps:
                    print(f"  - {name}")
                raise SystemExit(1)

            print("\n[check] Quality gate passed.")

        def _parse_args(self) -> argparse.Namespace:
            parser = argparse.ArgumentParser(description="Run local quality gate checks.")
            parser.add_argument(
                "--ci",
                action="store_true",
                help="Run full CI-like checks (integration + security).",
            )
            parser.add_argument(
                "--with-integration",
                action="store_true",
                help="Include integration tests without --ci.",
            )
            parser.add_argument(
                "--with-security",
                action="store_true",
                help="Include security checks without --ci.",
            )
            parser.add_argument(
                "--fail-fast",
                action="store_true",
                help="Stop on the first failed step.",
            )
            return parser.parse_args()

        def _build_steps(self, args: argparse.Namespace) -> list[CheckStep]:
            py = sys.executable
            include_integration = args.ci or args.with_integration
            include_security = args.ci or args.with_security

            steps = [
                CheckStep("Ruff lint", [py, "-m", "ruff", "check", "."]),
                CheckStep("Ruff format", [py, "-m", "ruff", "format", "--check", "."]),
                CheckStep("Mypy", [py, "-m", "mypy", "src"]),
                CheckStep(
                    "Unit tests",
                    [py, "-m", "pytest", "tests/", "-m", "unit", "-v", "--tb=short"],
                ),
            ]

            if include_integration:
                steps.append(
                    CheckStep(
                        "Integration tests",
                        [py, "-m", "pytest", "tests/", "-m", "integration", "-v", "--tb=short"],
                    )
                )

            if include_security:
                steps.extend(
                    [
                        CheckStep(
                            "Bandit",
                            [py, "-m", "bandit", "-q", "-c", "pyproject.toml", "-r", "src"],
                        ),
                        CheckStep("pip-audit", [py, "-m", "pip_audit"]),
                    ]
                )

            return steps


if __name__ == "__main__":
    CheckRunner(Path(__file__).parent.parent.parent).main()
