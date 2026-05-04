# Local Environment Setup Guide

This guide explains how to set up the dual-environment (Dev/Prod) system on a single machine using Docker Desktop and Prefect.

## 1. Infrastructure

Start all infrastructure services (databases, Prefect, Jenkins, CloudBeaver) using Docker Compose:
```bash
docker-compose --env-file dev.env up -d
```

This single command brings up:

| Service | Port | Container Name | Persistent Volume |
| :--- | :--- | :--- | :--- |
| **Dev Database** | `5434` | `timescaledb-dev` | `timescaledb_data_dev` |
| **Prod Database** | `5435` | `timescaledb-prod` | `timescaledb_data_prod` |
| **Prefect Server** | `4200` | `prefect-server` | `prefect_data` |
| **CloudBeaver** | `8978` | `cloudbeaver` | `cloudbeaver_data` |
| **Jenkins** | `8080` | `jenkins` | Bind mount: `jenkins_home/` |

## 2. Prefect Cluster (Fully Automated)

The Prefect stack is fully managed by Docker Compose with **zero manual steps**:

1. **`prefect-server`**: Starts the Prefect API and UI on port `4200`. Includes a healthcheck so dependent services wait until it's ready.
2. **`prefect-init`**: A one-shot container that automatically creates the work pools:
   - `dev-k8s-pool` (Type: `docker`)
   - `prod-k8s-pool` (Type: `docker`)
   - Uses `--if-not-exists` so it's safe to run repeatedly.
3. **`prefect-worker-dev`**: A persistent worker polling `dev-k8s-pool`. Installs `prefect-docker` and mounts the Docker socket.
4. **`prefect-worker-prod`**: A persistent worker polling `prod-k8s-pool`. Same configuration as the dev worker.

Access the UI: [http://localhost:4200](http://localhost:4200)

> **Note**: No manual `prefect server start` or `prefect worker start` commands are needed. Everything boots automatically with `docker-compose up -d`.

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
3. Triggering a `dev-` deployment will run the `:dev` image in the `dev-k8s-pool`, which is hardcoded to use the `dev` database.
