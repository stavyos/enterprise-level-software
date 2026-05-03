# Project Rules

## Source Control & Deployment
- **No Direct Pushes**: You are STRICTLY PROHIBITED from pushing code directly to the `master` or `main` branches.
- **Pull Request Only**: ALL changes MUST be performed in a feature branch (prefixed with `sy/`) and submitted via a Pull Request.
- **Workflow**: All changes must be performed in a feature branch and isolated within a git worktree. When creating a new worktree, copy relevant environment files (`dev.env`, `prod.env`) to the new worktree.
- **GEMINI Configuration**: When adding or updating information in `GEMINI.md` or `GEMINI.local.md`, you MUST do so in the **project root directory** and NOT within a git worktree to maintain a single source of truth.

## Environment & Infrastructure Management
- **Environment Isolation**: Strictly separate **Development (dev)** and **Production (prd)**. Note: Use `prd` (not `prod`) for consistency.
- **Databases (TimescaleDB)**:
    - **Dev**: Port `5434`. **Prd**: Port `5435`.
    - **Unified UI**: Port `8978` (**CloudBeaver**). Manage both connections from this single dashboard.
- **Storage Strategy (Hybrid Model)**:
    - **Postgres**: Store Metadata (Exchanges), News, and EOD data.
    - **Parquet**: Store high-volume **Intraday (1-minute)** data only.
    - **NTFS Path Mandate**: For Docker Desktop stability on Windows, use host NTFS paths (e.g., `C:/enterprise-level-software/data/dev`) and map them as `//c/path` in `JobVariables`.

## Engineering & Operational Standards
- **Fail-Fast Policy**: ALL ETL flows must raise `RuntimeError` on critical failures (API errors, DB issues, Storage errors). Never log and continue; ensure Prefect visibility.
- **API Limits & Chunking**:
    - **Intraday**: 1-minute requests MUST NOT exceed **120 calendar days**. Dispatchers must automatically chunk larger ranges.
    - **News**: Implement **pagination** (1000 items per batch) using `offset` to fetch deep history.
- **Type Safety**: Mandatory Python type hints (PEP 585/604). Postgres `ARRAY` type is preferred over `JSON` for performance in news symbols/tags.
- **Database Schema Integrity**:
    - The `volume` column in EOD and Adjusted tables MUST use `BigInteger` (SQL `BIGINT`) to prevent overflow for high-volume assets (e.g., AAPL).
    - Reference data flows (like `Exchanges`) should NOT include a `bus_date` parameter in the flow signature if the source API does not provide historical snapshots, as it implies non-existent historical tracking.

## Prefect Orchestration
- **Deployment Suffixing**: Register deployments with `ENV_PREFIX` (e.g., `Flow-Name/dev`).
- **Worker Configuration**: Start workers with `--type docker` using `uv run prefect worker start --pool dev-k8s-pool --type docker`.
- **Registration**: Use `RunnerDeployment.from_entrypoint` to ensure schema inference for CLI parameters.
- **CI/CD Secret Injection**: Secrets (API Keys, DB Passwords) must be managed via Jenkins credentials and injected during both the Docker build phase (`--build-arg`) and the deployment registration phase (`withEnv`). This ensures flows have access to credentials both at build-time and runtime.
