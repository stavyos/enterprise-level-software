# Prefect Orchestration

## Overview
We use **Prefect 3.x** as our workflow orchestration engine to manage, schedule, and monitor our ETL flows. Prefect provides a distributed system for executing Python tasks with built-in observability and error handling.

## Environment Architecture

We maintain strict separation between environments to ensure stable production runs while allowing experimental development.

| Feature | Development (Dev) | Production (Prod) |
| :--- | :--- | :--- |
| **API URL** | `http://127.0.0.1:4200/api` | `http://127.0.0.1:4201/api` |
| **Work Pool** | `dev-k8s-pool` | `prod-k8s-pool` |
| **Config File** | `.env.dev` | `.env.prod` |

## Infrastructure
- **Orchestrator Application**: Located in `apps/prefect-orchestrator`, this component manages the Prefect server and environment-specific workers.
- **Flow Implementation**: Flows are defined within the `etl-service` application in the `etl/flows` module.
- **Worker Infrastructure**: Flows are deployed as **Kubernetes Jobs** (managed via `prefect-kubernetes`), ensuring isolated and scalable execution.

## Key Concepts
- **Deployments**: We use the "Saver vs. Dispatcher" pattern. Dispatchers handle orchestration and chunking, while Savers handle the actual data processing.
- **Job Variables**: Resource specifications (CPU/Memory) are dynamically mapped to Kubernetes Job templates via `JobVariables` in the `etl/deployments_settings` module.

## Execution

### Development (Dev)
To start the Dev server and worker:
```bash
npx nx run prefect-orchestrator:start:dev
```
Access the UI at: `http://127.0.0.1:4200`

### Production (Prod)
To start the Prod server and worker:
```bash
npx nx run prefect-orchestrator:start:prod
```
Access the UI at: `http://127.0.0.1:4201`

## Configuration Management
This project uses **`python-dotenv`** to load environment variables for Nx targets. This ensures that the correct `PREFECT_API_URL` and database credentials are set before any Prefect command is executed.

Example for manual execution:
```bash
uv run dotenv -f .env.prod run -- prefect server start
```

## Getting Started
For a step-by-step guide to setting up your environment, see the [Setup Guide](./setup-guide.md).


### Concurrency Limits
We implement individual concurrency limits for each deployment type within the AbstractDeploymentSettings:
- **Savers**: 2 concurrent runs.
- **Dispatchers**: 1 concurrent run.

These limits are applied dynamically during the deployment registration process in `deploy_etls.py`.
