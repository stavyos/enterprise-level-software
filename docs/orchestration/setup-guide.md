# Kubernetes and Prefect Setup Guide

This guide outlines the steps to set up development and production environments using a shared Prefect cluster and isolated TimescaleDB instances.

## 1. Prerequisites
- **Docker Desktop**: With Kubernetes enabled.
- **uv**: Python package manager.
- **Node.js**: For the Nx CLI.
- **python-dotenv[cli]**: For environment variable management.

## 2. Infrastructure Setup (Databases)
**Action**: Start the isolated databases from the project root.
```bash
docker-compose up -d
```

| Environment | App DB Port | Container Name |
| :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` |
| **Production** | `5435` | `timescaledb-prod` |

## 3. Configuration
1. Copy `template.dev.env` to `dev.env`.
2. Copy `template.prod.env` to `prod.env`.
3. Update the `DB_USER`, `DB_PASSWORD`, and `EODHD_API_KEY` in both files.

## 4. Set Up Prefect Orchestrator
We use a single Prefect cluster for all environments.

```bash
# Start server and worker
npx nx run prefect-orchestrator:start
```

## 5. Configure Work Pool
After starting the Prefect server, create the Kubernetes Work Pool in the UI ([http://127.0.0.1:4200](http://127.0.0.1:4200)):
- Name: `my-k8s-pool`

## 6. Register Deployments
Register ETL flows with environment-specific prefixes.

```bash
# Register for Dev (prefixed with dev-)
npx nx run etl-service:deploy:dev

# Register for Prod (prefixed with prod-)
npx nx run etl-service:deploy:prod
```

## 7. Docker Build
Build the Docker images used by the workers.

```bash
# Build for Dev
npx nx run etl-service:docker-build:dev

# Build for Prod
npx nx run etl-service:docker-build:prod
```
