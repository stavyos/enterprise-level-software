# PR-8: Add Combined Prefect Start Command

## Purpose
This PR introduces a new `start` target to the `prefect-orchestrator` application, allowing developers to start both the Prefect server and the worker (activating the work pool) with a single command.

## Key Changes
- **`apps/prefect-orchestrator/project.json`**: Added a `start` target using `nx:run-commands` with `parallel: true` to execute both `run` and `worker` targets concurrently.
- **`apps/prefect-orchestrator/README.md`**: Updated the "Key Commands" section to include the new `npx nx run prefect-orchestrator:start` command.

## Date
Saturday, April 11, 2026
