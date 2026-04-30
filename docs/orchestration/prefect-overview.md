# Prefect Orchestration

## Overview
We use **Prefect 3.x** to manage, schedule, and monitor our ETL flows.

## Environment Architecture: Single Cluster, Multi-Tenant
To optimize local resources, we maintain a **single unified Prefect cluster** but achieve strict isolation at the data and execution layers.

### Isolation Pillars
1.  **Deployment Naming**: Every deployment is registered with an environment suffix (e.g., `EOD-Saver/dev`).
2.  **Isolated Databases**: Workers connect to different TimescaleDB instances (`5434` for dev, `5435` for prod).
3.  **Isolated Data Directories**: Parquet files are stored in environment-specific volumes (e.g., `data/dev` vs `data/prod`).
4.  **Baked Docker Images**: Environment variables are baked into the Docker images at build time, ensuring that an image tagged `:prod` can only talk to the production database and data volume.

| Feature | Development (Dev) | Production (Prod) |
| :--- | :--- | :--- |
| **Deployment Suffix** | `/dev` | `/prod` |
| **App DB Port** | `5434` | `5435` |
| **Data Directory** | `data/dev` | `data/prd` |
| **Docker Image** | `etl-service:dev` | `etl-service:prod` |
## Infrastructure
- **Orchestrator Application**: Manages the single Prefect server and worker.
- **Registration logic**: The `deploy_etls.py` script uses the `ENV_PREFIX` variable to configure the deployment name and metadata.

## Execution
Start the cluster:
```bash
npx nx run prefect-orchestrator:start
```
Access the UI: [http://localhost:4200](http://localhost:4200)
