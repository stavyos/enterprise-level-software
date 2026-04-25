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
