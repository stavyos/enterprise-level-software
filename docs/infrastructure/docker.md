# Docker Overview

## What is Docker?
**Docker** is used in this project to provide isolated, reproducible environments for our databases and ETL workers.

## How we use it here

### 1. Database Isolation
We use **Docker Compose** to run two independent **TimescaleDB** instances on different ports. This ensures that development data never bleeds into production.

| Environment | Port | Container Name | Persistent Volume |
| :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `timescaledb_data_dev` |
| **Production** | `5435` | `timescaledb-prod` | `timescaledb_data_prod` |

**Startup Command**:
```bash
docker-compose up -d
```

### 2. ETL Service Isolation
We build environment-specific images using the same `Dockerfile.etl`. By using build arguments, we bake the configuration directly into the image.

**Key Arguments**:
- `DB_PORT`: `5434` (Dev) vs `5435` (Prod).
- `ENV_PREFIX`: `dev` vs `prod`.

**Build Commands**:
- **Dev**: `npx nx run etl-service:docker-build:dev`
- **Prod**: `npx nx run etl-service:docker-build:prod`

## CI/CD Orchestration & Networking

### Shared Network
A dedicated Docker network, `enterprise-network`, facilitates secure communication between services:
- **Jenkins**: Performs builds and triggers deployments on this network.
- **Prefect Server**: Accessible at `http://prefect-server:4200/api` within the network.
- **Agent Containers**: Dynamic build agents (custom Node/Python images) join this network to register flows.

### Advanced: Docker-in-Docker
The Jenkins container has access to the host's Docker engine via a socket mount (`/var/run/docker.sock`). This allows it to build, tag, and run the ETL images as part of the automated pipeline.
