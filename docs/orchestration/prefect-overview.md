# Prefect Orchestration

## Overview
We use **Prefect 3.x** as our workflow orchestration engine to manage, schedule, and monitor our ETL flows. Prefect provides a distributed system for executing Python tasks with built-in observability and error handling.

## Architecture
- **Orchestrator Application**: Located in `apps/prefect-orchestrator`, this component manages the Prefect server and the local Work Pool (`my-k8s-pool`).
- **Flow Implementation**: Flows are defined within the `etl-service` application in the `etl/flows` module.
- **Worker Infrastructure**: Flows are deployed as **Kubernetes Jobs** (managed via `prefect-kubernetes`), ensuring isolated and scalable execution.

## Key Concepts
- **Deployments**: We use the "Saver vs. Dispatcher" pattern. Dispatchers handle orchestration and chunking, while Savers handle the actual data processing.
- **Job Variables**: Resource specifications (CPU/Memory) are dynamically mapped to Kubernetes Job templates via `JobVariables` in the `etl/deployments_settings` module.

## Local Execution
To start the Prefect server locally:
```bash
npx nx run prefect-orchestrator:run
```
Access the UI at: `http://127.0.0.1:4200`


To configure the local API URL:
``bash
uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
``


### Running a Worker
To activate the work pool and process jobs:
``bash
npx nx run prefect-orchestrator:worker
``


## Getting Started
For a step-by-step guide to setting up your local Kubernetes and Prefect environment, see the [Setup Guide](./setup-guide.md).


### Concurrency Limits
We implement individual concurrency limits for each deployment type within the AbstractDeploymentSettings: 
- **Savers**: 2 concurrent runs.
- **Dispatchers**: 1 concurrent run.

These limits are applied dynamically during the deployment registration process in deploy_etls.py.
