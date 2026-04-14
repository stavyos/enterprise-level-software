# Kubernetes and Prefect Setup Guide

This guide outlines the steps to set up development and production environments using Docker Desktop's Kubernetes, Prefect for workflow orchestration, and TimescaleDB.

## 1. Prerequisites
Before starting, ensure you have the following installed:
- **Docker Desktop**: With Kubernetes enabled.
- **uv**: Python package manager.
- **Node.js**: For the Nx CLI.
- **python-dotenv[cli]**: For environment variable management.

## 2. Infrastructure Setup (Databases)
We use Docker Compose to manage two separate TimescaleDB instances.

**Action**: Start the databases from the project root.
```bash
docker-compose up -d
```

| Instance | Port | Container Name |
| :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` |
| **Production** | `5435` | `timescaledb-prod` |

## 3. Configuration
1. Copy `template.env.dev` to `.env.dev`.
2. Copy `template.env.prod` to `.env.prod`.
3. Update the `DB_USER`, `DB_PASSWORD`, and `EODHD_API_KEY` in both files.

## 4. Set Up Prefect Orchestrator
We use environment-specific Nx targets to manage Prefect servers and workers.

### Development (Dev)
Starts the server on port `4200` and the worker for `dev-k8s-pool`.
```bash
# Start both server and worker
npx nx run prefect-orchestrator:start:dev

# Or start separately
npx nx run prefect-orchestrator:run:dev
npx nx run prefect-orchestrator:worker:dev
```

### Production (Prod)
Starts the server on port `4201` and the worker for `prod-k8s-pool`.
```bash
# Start both server and worker
npx nx run prefect-orchestrator:start:prod

# Or start separately
npx nx run prefect-orchestrator:run:prod
npx nx run prefect-orchestrator:worker:prod
```

## 5. Configure Work Pools
After starting the Prefect server, you must create the corresponding Kubernetes Work Pool in the UI.

1. **Dev UI**: [http://127.0.0.1:4200](http://127.0.0.1:4200) -> Create `dev-k8s-pool`.
2. **Prod UI**: [http://127.0.0.1:4201](http://127.0.0.1:4201) -> Create `prod-k8s-pool`.

## 6. Register Deployments
Register all ETL flows with the environment-specific Prefect server.

```bash
# Register for Dev
npx nx run etl-service:deploy:dev

# Register for Prod
npx nx run etl-service:deploy:prod
```

## 7. Docker Build
Build the environment-specific Docker images.

```bash
# Build for Dev
npx nx run etl-service:docker-build:dev

# Build for Prod
npx nx run etl-service:docker-build:prod
```

## Troubleshooting & Tips
- **Variable Loading**: We use `uv run dotenv -f <file> run -- <command>` to ensure the correct environment variables are loaded for each Nx target.
- **Image Pulls**: Since we are using a local cluster, ensure your Docker images are either built locally (and visible to the `docker-desktop` context) or hosted in an accessible registry.
- **Resources**: If a flow fails with `OOMKilled`, check the `JobVariables` in your deployment settings to increase Memory limits.
