"""
Quality gate for codex_tools library.
Adapted from the "Lily Project Quality Tool" style.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent.parent.parent
SRC_DIR = PROJECT_ROOT / "src"
TESTS_DIR = PROJECT_ROOT / "tests"
TOOLS_DIR = PROJECT_ROOT / "tools"

# Directories to check for Python tools (Ruff, Mypy)
PYTHON_DIRS = f"{SRC_DIR} {TOOLS_DIR}"


# ANSI Colors
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"


def print_step(msg: str) -> None:
    print(f"\n{Colors.YELLOW}🔍 {msg}...{Colors.ENDC}")


def print_success(msg: str) -> None:
    print(f"{Colors.GREEN}✅ {msg}{Colors.ENDC}")


def print_error(msg: str) -> None:
    print(f"{Colors.RED}❌ {msg}{Colors.ENDC}")


def run_command(command: str, cwd: Path = PROJECT_ROOT, capture_output: bool = False) -> tuple[bool, str]:
    """Runs a system command and returns result."""
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            check=False,
            text=True,
            capture_output=capture_output,
        )
        return result.returncode == 0, result.stdout or result.stderr or ""
    except Exception as e:
        return False, str(e)


# --- Check Functions ---


def check_linters() -> bool:
    print_step("Running Linters (Ruff & Pre-commit hooks)")

    # --- Auto-fixing and formatting with Ruff ---
    print("Attempting to auto-fix Ruff issues...")
    fix_success, _ = run_command(f"ruff check {PYTHON_DIRS} --fix")
    if not fix_success:
        print_error("Ruff auto-fix command failed.")
        return False
    print_success("Ruff auto-fix completed.")

    print("Attempting to auto-format with Ruff...")
    format_success, _ = run_command(f"ruff format {PYTHON_DIRS}")
    if not format_success:
        print_error("Ruff auto-format command failed.")
        return False
    print_success("Ruff auto-format completed.")

    # --- Verification checks after auto-fixing/formatting ---
    print("Verifying Ruff check (no fixable issues remaining)...")
    ruff_check_success, ruff_check_out = run_command(f"ruff check {PYTHON_DIRS}", capture_output=True)
    if not ruff_check_success:
        print_error(f"Ruff check failed (unfixable issues or issues after fix):\n{ruff_check_out}")
        return False
    print_success("Ruff check passed.")

    print("Verifying Ruff format (no formatting issues remaining)...")
    ruff_format_check_success, ruff_format_check_out = run_command(
        f"ruff format {PYTHON_DIRS} --check", capture_output=True
    )
    if not ruff_format_check_success:
        print_error(f"Ruff format check failed (files still need formatting):\n{ruff_format_check_out}")
        return False
    print_success("Ruff format check passed.")

    print("Running pre-commit hooks...")
    # These hooks will check all files based on .pre-commit-config.yaml
    # We run them via 'pre-commit run --all-files' to be thorough
    success, out = run_command("pre-commit run --all-files")
    if not success:
        print_error(f"Pre-commit hooks failed:\n{out}")
        return False
    print_success("Pre-commit hooks passed.")

    return True


def check_types() -> bool:
    print_step("Checking Types (Mypy)")
    # Mypy uses .mypy_cache for incremental checks.
    # It will only re-check files that changed or are affected by changes.
    success, out = run_command(f"mypy {SRC_DIR}", capture_output=True)
    if not success:
        print_error(f"Mypy check failed:\n{out}")
    else:
        print_success("Mypy check passed.")
    return success


def run_tests() -> bool:
    print_step("Running Unit Tests (Pytest)")
    success, _ = run_command(f"pytest {TESTS_DIR} -v --tb=short")
    if success:
        print_success("All tests passed.")
    else:
        print_error("Tests failed.")
    return success


def check_security_deep() -> bool:
    """Deep security audit: dependencies + static analysis."""
    print_step("Deep Security Audit")

    print("Checking for vulnerable dependencies (pip-audit)...")
    success, out = run_command("pip-audit", capture_output=True)
    if not success:
        print_error(f"Security vulnerabilities found in packages:\n{out}")
        return False

    print("Running Bandit (SAST)...")
    # -r for recursive, -ll to show only medium/high severity
    success, out = run_command(f"bandit -r {SRC_DIR} -ll", capture_output=True)
    if not success:
        print_error(f"Bandit found security risks:\n{out}")
        return False

    print_success("Security audit passed.")
    return True


# --- Main Logic ---


def run_all() -> None:
    # Clear screen for fresh output
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    print(f"{Colors.HEADER}{Colors.BOLD}=== codex_tools quality gate ==={Colors.ENDC}")

    if not check_linters():
        sys.exit(1)
    if not check_types():
        sys.exit(1)
    if not check_security_deep():
        sys.exit(1)

    # Prompt for tests
    test_choice = input(f"\n{Colors.YELLOW}🚀 Run Unit Tests? [y/N]: {Colors.ENDC}").strip().lower()
    if test_choice == "y":
        if not run_tests():
            sys.exit(1)
    else:
        print(f"{Colors.BLUE}ℹ️ Skipping Unit Tests.{Colors.ENDC}")

    print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL CHECKS PASSED! You are ready to push.{Colors.ENDC}")


def interactive_menu() -> None:
    while True:
        print(f"\n{Colors.CYAN}{Colors.BOLD}🛠 codex_tools Quality Tool{Colors.ENDC}")
        print("1. Fast Check (Lint & Pre-commit)")
        print("2. Type Check (Mypy)")
        print("3. Run Unit Tests")
        print("4. Deep Security Audit (Bandit + pip-audit)")
        print("5. Run Everything")
        print("0. Exit")

        choice = input(f"\n{Colors.YELLOW}Select an option [5]: {Colors.ENDC}").strip() or "5"

        if choice == "1":
            check_linters()
        elif choice == "2":
            check_types()
        elif choice == "3":
            run_tests()
        elif choice == "4":
            check_security_deep()
        elif choice == "5":
            run_all()
        elif choice == "0":
            break
        else:
            print_error("Invalid choice")


def main() -> None:
    parser = argparse.ArgumentParser(description="codex_tools quality gate")
    parser.add_argument("--all", action="store_true", help="Run all checks")
    parser.add_argument("--lint", action="store_true", help="Run linters only")
    parser.add_argument("--types", action="store_true", help="Run type check only")
    parser.add_argument("--tests", action="store_true", help="Run tests only")
    parser.add_argument("--security", action="store_true", help="Run security audit only")
    parser.add_argument("--menu", action="store_true", help="Open interactive menu")
    args = parser.parse_args()

    if args.all:
        run_all()
    elif args.lint:
        sys.exit(0 if check_linters() else 1)
    elif args.types:
        sys.exit(0 if check_types() else 1)
    elif args.tests:
        sys.exit(0 if run_tests() else 1)
    elif args.security:
        sys.exit(0 if check_security_deep() else 1)
    elif args.menu:
        interactive_menu()
    else:
        # Default to interactive menu if no args
        interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}Aborted by user.{Colors.ENDC}")
        sys.exit(1)
