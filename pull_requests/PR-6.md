# PR-6: Migrate to Ruff & Setup Pre-commit Hooks

## Purpose
This PR streamlines the monorepo's code quality tooling by migrating from multiple tools (Black, isort, Flake8) and a custom linter tool to a unified, high-performance setup using **Ruff**. It also introduces **pre-commit** hooks to enforce these standards automatically.

## Key Changes

### 1. Tooling Consolidation
- **Ruff**: Integrated Ruff as the primary linter and formatter. Configuration is centralized in the root `pyproject.toml`.
- **Pre-commit**: Added `.pre-commit-config.yaml` to run Ruff (format and lint) and other standard hooks (trailing whitespace, end-of-file, etc.) on every commit.
- **Decommissioned Tools**:
  - Deleted `.flake8`.
  - Removed the entire `tools/linter` package.
  - Removed Black and isort configurations.

### 2. Nx Integration
- Updated `nx.json` with new `lint` and `format` targets that use `uvx ruff check .` and `uvx ruff format .`.
- Removed dependencies on the deleted `linter` project from all project targets.

### 3. Code Quality Improvements
- Fixed various linting issues uncovered by Ruff across the codebase:
  - **UP038**: Modernized `isinstance` calls to use `|` instead of tuples.
  - **B007**: Fixed unused loop control variables.
  - **B904**: Added `from err` to exception raising for proper chaining.
  - **E501**: Wrapped overly long lines in documentation comments.
- Performed a global reformat of the codebase to match the new Ruff standard.

### 4. Documentation
- Updated `README.md` with new developer commands and pre-commit instructions.
- Updated the Tech Learning Center (`docs/`) to reflect the move to Ruff and unified tooling.

## Verification Results
- `uvx pre-commit run --all-files`: **Passed**
- `npx nx run-many -t lint`: **Passed**
- `npx nx run-many -t test`: **Passed**

## Date
Saturday, April 11, 2026
