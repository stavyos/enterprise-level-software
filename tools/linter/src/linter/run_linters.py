"""Run all linters for a given project."""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, and stderr."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    stdout = result.stdout if result.stdout is not None else ""
    stderr = result.stderr if result.stderr is not None else ""
    return result.returncode, stdout, stderr


def run_flake8(project_path: Path, check_only: bool = True) -> tuple[int, str]:
    """Run flake8 on the project."""
    print(f"Running flake8 on {project_path}...")
    cmd = ["flake8", "src"]
    if (project_path / "tests").exists():
        cmd.append("tests")

    exit_code, stdout, stderr = run_command(cmd, project_path)
    output = stdout + stderr

    if exit_code != 0:
        print(f"[FAIL] flake8 found issues:\n{output}")
    else:
        print("[PASS] flake8 passed")

    return exit_code, output


def run_black(project_path: Path, check_only: bool = True) -> tuple[int, str]:
    """Run black on the project."""
    print(f"Running black on {project_path}...")
    cmd = ["black", "src"]
    if (project_path / "tests").exists():
        cmd.append("tests")

    if check_only:
        cmd.extend(["--check", "--diff"])

    exit_code, stdout, stderr = run_command(cmd, project_path)
    output = stdout + stderr

    if exit_code != 0:
        if check_only:
            print(f"[FAIL] black found formatting issues:\n{output}")
        else:
            print(f"[DONE] black formatted files:\n{output}")
    else:
        print("[PASS] black passed")

    return exit_code, output


def run_isort(project_path: Path, check_only: bool = True) -> tuple[int, str]:
    """Runs isort on the project"""
    print(f"Running isort on {project_path}...")
    cmd = ["isort", "."]

    if check_only:
        cmd.append("--check-only")
        cmd.append("--diff")

    exit_code, stdout, stderr = run_command(cmd, project_path)
    output = stdout + stderr

    if exit_code != 0:
        if check_only:
            print(f"[FAIL] isort found import sorting issues:\n{output}")
        else:
            print(f"[DONE] isort sorted imports:\n{output}")
    else:
        print("[PASS] isort passed")

    return exit_code, output


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run linters on a project")
    parser.add_argument("project_path", help="Path to the project to lint")
    parser.add_argument("--fix", action="store_true", help="Fix issues instead of just checking")

    args = parser.parse_args()
    project_path = Path(args.project_path).resolve()

    if not project_path.exists():
        print(f"Error: Project path {project_path} does not exist")
        sys.exit(1)

    print(f"{'-' * 60}")
    print(f"Linting {project_path.name}")
    print(f"{'-' * 60}\n")

    check_only = not args.fix
    exit_codes = []

    # Run all linters
    exit_code, _ = run_flake8(project_path, check_only)
    exit_codes.append(exit_code)

    exit_code, _ = run_black(project_path, check_only)
    exit_codes.append(exit_code)

    exit_code, _ = run_isort(project_path, check_only)
    exit_codes.append(exit_code)

    # Exit with error if any linter failed
    if any(code != 0 for code in exit_codes):
        print(f"\n[FAIL] Linting failed for {project_path.name}")
        sys.exit(1)
    else:
        print(f"\n[PASS] All linters passed for {project_path.name}")
        sys.exit(0)


if __name__ == "__main__":
    main()
