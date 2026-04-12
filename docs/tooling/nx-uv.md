# Monorepo Management & Tooling

To maintain an enterprise-grade codebase, we use a modern stack of tools that ensure speed, reproducibility, and high developer velocity.

## Nx: The Workspace Orchestrator

While [Nx](https://nx.dev) is traditionally associated with JavaScript/TypeScript, we use it as our central command hub for this Python monorepo.

### Core Concepts
- **Workspace Structure**: Projects are split into `apps/` (deployable services) and `libs/` (reusable logic).
- **`project.json`**: Every project has this file defining its "targets" (commands like `test`, `lint`, `deploy`).
- **Task Orchestration**: Nx allows us to run commands across multiple projects efficiently.

**Example: Running all tests**
```bash
npx nx run-many -t test
```

### Why Nx?
- **Consistency**: All projects, regardless of their internal logic, are managed with the same set of commands.
- **Dependency Graph**: Nx understands which libs are used by which apps, allowing for optimized CI/CD (e.g., only testing what changed).

## UV: Modern Python Dependency Management

We use [uv](https://github.com/astral-sh/uv) for all Python-related tasks. It is a blazing-fast Python package installer and resolver written in Rust.

### Key Benefits
- **Speed**: `uv` is often 10-100x faster than `pip` or `poetry`.
- **Reproducibility**: The `uv.lock` file ensures that every developer and production environment uses the exact same versions of every dependency.
- **Venv Management**: `uv` handles virtual environment creation and syncing automatically.

### Workspace Usage
- **Root `pyproject.toml`**: Manages workspace-wide settings and tools like **Ruff**.
- **Project `pyproject.toml`**: Each app and lib defines its specific dependencies.

**Common Commands:**
- **Add a dependency**: `uv add <package>` (run within the project folder).
- **Run a script**: `uv run python <script.py>`.
- **Sync environments**: `uv sync`.

## Ruff: Fast & Unified Linting

We use [Ruff](https://github.com/astral-sh/ruff) as our single tool for both linting and formatting — it replaces Flake8, isort, and Black.

### Why Ruff?
- **Speed**: It is written in Rust and is orders of magnitude faster than traditional Python linters.
- **Unified**: Replaces multiple tools with a single configuration in the root `pyproject.toml`.
- **Pre-commit integration**: Ensures code quality before it even reaches a Pull Request.

## Pre-commit Hooks

To ensure consistency across the monorepo, we use [pre-commit](https://pre-commit.com/) to run Ruff and other checks automatically during `git commit`.

### Setup
Run the following command once to install the hooks in your local Git repository:
```bash
uvx pre-commit install
```

### Manual Execution
You can run the hooks on all files at any time:
```bash
uvx pre-commit run --all-files
```
