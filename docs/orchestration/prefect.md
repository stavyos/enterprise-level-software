# Workflow Orchestration Strategy

Our system uses a two-tier architecture (Dispatcher/Saver) to handle high-volume financial data acquisition.

## The Image-Baking Pattern
To maintain environment isolation within a single cluster, we use the **Image-Baking** pattern.

### 1. Build Phase
We use Docker build arguments (`--build-arg`) to inject environment-specific database credentials and prefixes into the image.
- `etl-service:dev`: Baked with Port 5434.
- `etl-service:prod`: Baked with Port 5435.

### 2. Registration Phase (Portable Strategy)
Deployment registration is handled in `apps/etl-service/src/etl_service/etl/deploy_etls.py`. We use a **Portable Deployment Strategy** to ensure flows registered from a development machine (Windows) work perfectly in production environments (Linux).

1.  **`flow.deploy(build=False)`**: We use the modern Prefect `flow.deploy` API. By setting `build=False`, we prevent Prefect from attempting to rebuild the image or pull code from the local filesystem.
2.  **Post-Registration Update**: After the deployment is registered, we explicitly clear the `path` and `pull_steps` attributes using the Prefect Client. This forces the worker to use the code **already baked into the container image** at the `PYTHONPATH` location, effectively making the deployment environment-agnostic.

### Job Variables & Infrastructure Hardening
Our `JobVariables` logic ensures that infrastructure-specific configuration (like Docker volumes) is correctly applied:
- **Volume Translation**: Automatically converts Windows drive paths (e.g., `C:/path`) to Docker-compatible forward-slash paths (`//c/path`).
- **Network Isolation**: Forces all ETL containers onto the `enterprise-network` to allow resolution of `host.docker.internal` for database access.
## Key Benefits
- **Zero Configuration Leakage**: Dev workers cannot accidentally connect to the Prod database because the connection logic is isolated within the image.
- **Unified Observability**: View all environment runs in a single dashboard while keeping them logically separated.
- **Path Portability**: The manual `RunnerDeployment` fix ensures that our Windows-based development environment can successfully trigger flows in Linux-based containers.

## Automated Deployments (CI/CD)
The entire registration process is automated via **Jenkins**:
- **Branch Detection**: PRs automatically register flows with the `dev` prefix.
- **Production Lifecycle**: Merges to `master` trigger the build and registration of `prod` deployments.
- **Self-Healing**: The pipeline ensures work pools exist and deployment metadata is always in sync with the latest container image.
