# Prefect Orchestration

## Overview
We use **Prefect 3.x** as our workflow orchestration engine to manage, schedule, and monitor our ETL flows.

## Environment Architecture

We use a **single Prefect cluster** for both Development and Production. Isolation is achieved by:
1.  **Deployment Prefixing**: Deployments are named `dev-flow-name` or `prod-flow-name`.
2.  **Database Routing**: The workers connect to different TimescaleDB instances based on the environment variables.

| Feature | Shared Value |
| :--- | :--- |
| **API URL** | `http://127.0.0.1:4200/api` |
| **Work Pool** | `my-k8s-pool` |

## Infrastructure
- **Orchestrator Application**: Manages the single Prefect control plane and Kubernetes worker.
- **Flow Implementation**: Defined within the `etl-service` application.
- **Deployment logic**: The `deploy_etls.py` script automatically reads the `ENV_PREFIX` and configures the deployment names.

## Execution

To start the cluster:
```bash
npx nx run prefect-orchestrator:start
```

## Configuration Management
This project uses **`python-dotenv`** to load environment variables for Nx targets. This ensures that the correct database credentials and environment prefix are set before any command is executed.

Example for manual registration:
```bash
uv run dotenv -f prod.env run -- python -m etl_service.etl.deploy_etls
```
