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
Start the unified Prefect server and worker:
```bash
npx nx run prefect-orchestrator:start
```
*Note: Ensure you have created the `my-k8s-pool` in the UI at http://localhost:4200/work-pools.*

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
Register your flows with the cluster. Each deployment will be suffixed with `/dev` or `/prod`.

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
2. You will see deployments like `EOD-Saver/dev` and `EOD-Saver/prod`.
3. Triggering a `/dev` deployment will run the `:dev` image, which is hardcoded to use the `dev` database.
