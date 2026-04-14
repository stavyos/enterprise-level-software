# Project Rules

## Source Control & Deployment
- **No Direct Pushes:** You are STRICTLY PROHIBITED from pushing code directly to the `master` or `main` branches. NEVER push to these branches.
- **Pull Request Only:** ALL changes, including documentation and configuration updates, MUST be performed in a feature branch (prefixed with `sy/`) and submitted via a Pull Request.
- **No Autonomous Merges:** You must never merge a Pull Request (PR) or perform a git merge into a protected branch on your own.
- **Workflow:** All changes must be performed in a feature branch and isolated within a git worktree as per global instructions. When creating a new worktree, you MUST also copy relevant `.env` files from the root or parent directory to the new worktree to ensure consistent local configuration. Final merging and pushing to the primary branch must be handled by the user.

## Engineering Standards
- **Documentation & Docstrings:** ALWAYS add comprehensive docstrings to all new or modified classes and methods. Docstrings must include a clear description of purpose, parameters (Args), and return values (Returns) following standard Python conventions (e.g., Google or Sphinx style).
- **Type Hinting:** Mandatory use of Python type hints for all function/method parameters and return values. Ensure modern PEP 585/604 syntax (e.g., `list[str]` instead of `List[str]`, `X | Y` instead of `Union[X, Y]`).

## Documentation & Tech Learning Center
- **Folder Structure:** This project maintains a `docs/` folder acting as a \"Tech Learning Center.\" All major technologies, architectural decisions, and third-party integrations MUST be documented here.
- **Organization:** Documentations must be logically grouped (e.g., `docs/python/`, `docs/database/`). Language-specific libraries should be nested under their respective language folder (e.g., `docs/python/packages/`).
- **Standardized Content:** Documentation files should explain *what* the tech is, *why* we use it, and *how* it is implemented/configured in this specific project.
- **Validation:** Before finalizing a Pull Request, you MUST run the `docs-validator` skill to ensure all new technologies and code changes are properly represented in the `docs/` folder.
- **PR Links:** When creating or updating a PR, always check if new documentation is required or if existing docs need updates to stay in sync with the code.

## Pull Request Documentation
- **Summary File:** For every new Pull Request, you MUST create a summary markdown file in the `pull_requests/` directory (e.g., `PR-1.md`, `PR-2.md`, etc.).
- **Content:** The summary should include:
  - A clear title and purpose of the PR.
  - A **Reviewer Reading Guide** providing a logical order to review the files.
  - A detailed list of key changes.
  - A Mermaid graph to visualize architectural changes or workspace dependencies if applicable.
  - The date of creation.
- **Continuous Updates:** You MUST update the corresponding `PR-X.md` file whenever you make changes to the code within a PR to ensure the documentation stays in sync with the implementation.
- **GitHub CLI:** You may use the `gh` CLI to create and manage pull requests directly. When creating a PR, use the corresponding summary file as the body (e.g., `gh pr create --title \"...\" --body-file pull_requests/PR-X.md`).
- **Permission to Open PR:** You MUST ALWAYS ask the user for explicit permission before opening a new Pull Request on GitHub. Do not automate the creation of PRs without a direct confirmation.

## Operational Rules
- **Prefect Orchestration:** When starting the Prefect server, always ensure the `my-k8s-pool` work pool worker is running to process Kubernetes-based flow runs.
- **Prefect CLI Operations:**
    - **Context Awareness**: ALWAYS execute Prefect CLI commands from within the specific application directory (e.g., `apps/etl-service` or `apps/prefect-orchestrator`) where the virtual environment and `prefect` dependency reside.
    - **Querying Flow Runs**: Use `uv run prefect flow-run ls --limit <N>` to list recent runs. Note that `--sort` is often NOT supported in the local CLI version; rely on the default chronological order.
    - **Retrieving Logs**: Use `uv run prefect flow-run logs <UUID>` to fetch logs. If logs are large, use PowerShell pipes like `| Select-Object -Last 20` or `| Select-String "..."` for targeted analysis.
    - **UUID Verification**: When extracting UUIDs from tables or logs, ensure the full ID is captured (not truncated) to avoid `ObjectNotFound` errors.
