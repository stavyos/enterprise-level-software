# Monorepo Management & Tooling

To maintain an enterprise-grade codebase, we use a modern stack of tools that ensure speed, reproducibility, and high developer velocity.

## Nx: The Workspace Orchestrator

While [Nx](https://nx.dev) is traditionally associated with JavaScript/TypeScript, we use it as our central command hub for this Python monorepo.

### Core Concepts
- **Workspace Structure**: Projects are split into `apps/` (deployable services) and `libs/` (reusable logic).
- **`project.json`**: Every project has this file defining its "targets" (commands like `test`, `lint`, `deploy`).
- **Task Orchestration**: Nx allows us to run commands across multiple projects efficiently.

## UV: Modern Python Dependency Management

We use [uv](https://github.com/astral-sh/uv) for all Python-related tasks. It is a blazing-fast Python package installer and resolver written in Rust.

## Python-Dotenv: Environment Management

To manage multiple environments (Dev/Prod) within the same monorepo, we use the **`python-dotenv`** CLI.

### Integration with Nx
We wrap our Nx targets with `dotenv run` to ensure the correct environment variables are loaded for each command.

**Example from `project.json`:**
```json
"run:prod": {
  "executor": "nx:run-commands",
  "options": {
    "command": "uv run dotenv -f ../../prod.env run -- prefect server start --port 4201"
  }
}
```

## Ruff: Fast & Unified Linting

We use [Ruff](https://github.com/astral-sh/ruff) as our single tool for both linting and formatting — it replaces Flake8, isort, and Black.

## Pre-commit Hooks

To ensure consistency across the monorepo, we use [pre-commit](https://pre-commit.com/) to run Ruff and other checks automatically during `git commit`.
