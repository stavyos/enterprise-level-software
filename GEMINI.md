# Project Rules

## Source Control & Deployment
- **No Direct Pushes**: You are STRICTLY PROHIBITED from pushing code directly to the `master` or `main` branches.
- **Pull Request Only**: ALL changes MUST be performed in a feature branch (prefixed with `sy/`) and submitted via a Pull Request.
- **Workflow**: All changes must be performed in a feature branch and isolated within a git worktree. When creating a new worktree, copy relevant environment files (`dev.env`, `prod.env`) to the new worktree.

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
- **Prefect Worker**: Ensure the `my-k8s-pool` is created in the Prefect UI to process flows.
- **CLI Context**: Execute Prefect commands from the specific application directory where dependencies reside.
