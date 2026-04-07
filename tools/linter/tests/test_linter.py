from pathlib import Path

from linter.run_linters import run_black, run_flake8, run_isort


def get_project_root() -> Path:
    """Get the project root directory by looking for pyproject.toml."""
    current_path = Path(__file__).resolve()
    project_root = None

    for parent in current_path.parents:
        if (parent / "pyproject.toml").exists():
            project_root = parent
            break

    if project_root is None:
        raise FileNotFoundError("Could not find project root (pyproject.toml not found)")

    return project_root


def test_flake8():
    """Test that flake8 passes on the linter tool source and tests."""
    project_root = get_project_root()
    exit_code, output = run_flake8(project_root, check_only=True)
    assert exit_code == 0, f"flake8 failed with output:\n{output}"


def test_formatted():
    """Test that black formatting is applied correctly."""
    project_root = get_project_root()
    exit_code, output = run_black(project_root, check_only=True)
    assert exit_code == 0, f"black formatting check failed with output:\n{output}"


def test_isort():
    """Test that import sorting is correct."""
    project_root = get_project_root()
    exit_code, output = run_isort(project_root, check_only=True)
    assert exit_code == 0, f"isort check failed with output:\n{output}"
