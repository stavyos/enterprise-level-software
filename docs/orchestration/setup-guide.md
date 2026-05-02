# Local Environment Setup Guide

This guide explains how to set up the dual-environment (Dev/Prod) system on a single machine using Docker Desktop and Prefect.

## 1. Infrastructure
Start the isolated databases using Docker Compose:
```bash
docker-compose up -d
```

| Database | Port | Container Name |
| :--- | :--- | :--- |
| **Dev** | `5434` | `timescaledb-dev` |
| **Prod** | `5435` | `timescaledb-prod` |

## 2. Prefect Cluster
Start the unified Prefect server and the relevant environment worker:

### Dev Stack
```bash
npx nx run prefect-orchestrator:start
```

### Prod Stack
```bash
npx nx run prefect-orchestrator:start:prod
```

*Note: You must create the work pools in the UI (or CLI) if they don't exist:*
- `dev-k8s-pool` (Type: `docker`)
- `prod-k8s-pool` (Type: `docker`)

## 3. Image Isolation
We bake environment settings into Docker images to ensure data isolation.

### Build Dev Image
```bash
npx nx run etl-service:docker-build:dev
```

### Build Prod Image
```bash
npx nx run etl-service:docker-build:prod
```

## 4. Deployment Registration
Register your flows with the cluster. Each deployment will be prefixed with `dev-` or `prod-`.

### Register Dev Deployments
```bash
npx nx run etl-service:deploy:dev
```

### Register Prod Deployments
```bash
npx nx run etl-service:deploy:prod
```

## 5. Running Flows
1. Open the [Prefect Dashboard](http://localhost:4200/deployments).
2. You will see deployments like `dev-EOD-Saver` and `prod-EOD-Saver`.
Triggering a `dev-` deployment will run the `:dev` image in the `dev-k8s-pool`, which is hardcoded to use the `dev` database.

## 6. Database Management
Access the web-based UI to manage your data:
- **Database UI**: [http://localhost:8978](http://localhost:8978)

Login credentials can be found in the [Database Architecture](../database/timescaledb.md) guide.
