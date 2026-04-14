# Prefect Orchestration

## Overview
We use **Prefect 3.x** as our workflow orchestration engine to manage, schedule, and monitor our ETL flows. Prefect provides a distributed system for executing Python tasks with built-in observability and error handling.

## Environment Architecture

We maintain strict separation between environments to ensure stable production runs while allowing experimental development.

| Feature | Development (Dev) | Production (Prod) |
| :--- | :--- | :--- |
| **API URL** | `http://127.0.0.1:4200/api` | `http://127.0.0.1:4201/api` |
| **Work Pool** | `dev-k8s-pool` | `prod-k8s-pool` |
| **Config File** | `dev.env` | `prod.env` |
| **Meta DB Port** | `5436` | `5437` |

## Infrastructure
- **Orchestrator Application**: Located in `apps/prefect-orchestrator`, this component manages the Prefect server and environment-specific workers.
- **Flow Implementation**: Flows are defined within the `etl-service` application in the `etl/flows` module.
- **Worker Infrastructure**: Flows are deployed as **Kubernetes Jobs** (managed via `prefect-kubernetes`), ensuring isolated and scalable execution.

## Execution

### Development (Dev)
To start the Dev cluster:
```bash
npx nx run prefect-orchestrator:start:dev
```

### Production (Prod)
To start the Prod cluster:
```bash
npx nx run prefect-orchestrator:start:prod
```

## Configuration Management
This project uses **`python-dotenv`** to load environment variables for Nx targets. This ensures that the correct `PREFECT_API_DATABASE_CONNECTION_URL` and database credentials are set before any Prefect command is executed.

Example for manual execution:
```bash
uv run dotenv -f prod.env run -- prefect server start
```

## Getting Started
For a step-by-step guide to setting up your environment, see the [Setup Guide](./setup-guide.md).
