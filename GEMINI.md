# Project Rules

## Source Control & Deployment
- **No Direct Pushes:** You are STRICTLY PROHIBITED from pushing code directly to the `master` or `main` branches. NEVER push to these branches.
- **Pull Request Only:** ALL changes, including documentation and configuration updates, MUST be performed in a feature branch (prefixed with `sy/`) and submitted via a Pull Request.
- **No Autonomous Merges:** You must never merge a Pull Request (PR) or perform a git merge into a protected branch on your own.
- **Workflow**: All changes must be performed in a feature branch and isolated within a git worktree as per global instructions. When creating a new worktree, you MUST also copy relevant `.env` files (e.g., `dev.env`, `prod.env`) from the root or parent directory to the new worktree to ensure consistent local configuration. Final merging and pushing to the primary branch must be handled by the user.
- **GEMINI Configuration**: When adding or updating information in `GEMINI.md` or `GEMINI.local.md`, you MUST do so in the **project root directory** and NOT within a git worktree to maintain a single source of truth for instructions and credentials.

## Environment & Infrastructure Management
- **Environment Isolation**: This project maintains strict separation between **Development (dev)** and **Production (prod)** data.
- **Databases (TimescaleDB)**:
    - **Dev Instance**: Port `5434` (`timescaledb-dev`).
    - **Prod Instance**: Port `5435` (`timescaledb-prod`).
    - Use `docker-compose up -d` to manage both.
- **Prefect Orchestration**:
    - A **single Prefect cluster** (port `4200`) is used for all environments.
    - **Isolation via Docker**: Isolation is enforced by building environment-specific images (`etl-service:dev` and `etl-service:prod`) where configuration is baked-in at build time.
    - **Deployment Suffixing**: Deployments must be registered with an environment suffix (e.g., `Flow-Name/dev`) using the `ENV_PREFIX` variable.

## Configuration Management
- **Environment Files**: Use `dev.env` and `prod.env` for local variable storage. These are ignored by git.
- **Templates**: For any new environment variable, you MUST update `template.dev.env` and `template.prod.env` with descriptions and placeholders.
- **Image Baking**: Use `--build-arg` during Docker builds to permanently set environment variables within the image.

## Engineering Standards
- **Documentation & Docstrings**: ALWAYS add comprehensive docstrings to all new or modified classes and methods (Google or Sphinx style).
- **Type Hinting**: Mandatory use of Python type hints (PEP 585/604 syntax).

## Documentation & Tech Learning Center
- **Folder Structure**: This project maintains a `docs/` folder ("Tech Learning Center"). All major technologies and architectural decisions MUST be documented here.
- **Validation**: Before finalizing a PR, run the `docs-validator` skill to ensure documentation is synchronized with code changes.

## Pull Request Documentation
- **Summary File**: For every PR, create a summary in `pull_requests/PR-X.md`.
- **Content**: Include Purpose, Reviewer Reading Guide, Key Changes, and an Architecture Diagram if applicable.

## Operational Rules
- **Prefect Server**: Always run the Prefect server in the background to ensure availability for workers and deployments.
- **Prefect Worker**:
    - Use environment-specific work pools: `dev-k8s-pool` and `prod-k8s-pool`.
    - Workers MUST be started with the `docker` type (requires `prefect-docker` package).
    - Example: `uv run prefect worker start --pool dev-k8s-pool --type docker`.
- **Flow Execution**: Prefer triggering `Dispatcher` deployments over `Saver` deployments for manual runs, as they handle default parameters (like `bus_date`) and orchestration.
- **Deployment Registration**:
    - Use `RunnerDeployment.from_entrypoint` in `deploy_etls.py` to ensure Prefect correctly infers and populates the `parameter_openapi_schema`.
    - This is critical for deployments that accept parameters (like `tickers` in `Main` dispatcher).
- **Environment Detection**: Avoid checking `sys.argv[0]` or the full script path for environment strings (like "prod"), as worktree directory names can cause false positives. Always slice `sys.argv[1:]` or use `ENV_PREFIX`.
- **Network Connectivity**: Flow runs inside Docker containers must use `host.docker.internal` to reach the TimescaleDB instances running on the host machine.
- **CLI Parameter Syntax**: When passing arrays via CLI (e.g., `tickers`), use the format `--param 'tickers=["AAPL","MSFT"]'`. If parsing fails, use a JSON file with `--params file.json`.
- **CLI Context**: Execute Prefect commands from the specific application directory where dependencies reside.
