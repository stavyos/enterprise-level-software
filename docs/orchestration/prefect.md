# Workflow Orchestration Strategy

Our system uses a two-tier architecture (Dispatcher/Saver) to handle high-volume financial data acquisition.

## The Image-Baking Pattern
To maintain environment isolation within a single cluster, we use the **Image-Baking** pattern.

### 1. Build Phase
We use Docker build arguments (`--build-arg`) to inject environment-specific database credentials and prefixes into the image.
- `etl-service:dev`: Baked with Port 5434.
- `etl-service:prod`: Baked with Port 5435.

### 2. Registration Phase
Deployment registration is handled in `apps/etl-service/src/etl_service/etl/deploy_etls.py`.

<<<<<<< Updated upstream
We use `RunnerDeployment.from_entrypoint` to ensure Prefect correctly infers and populates the `parameter_openapi_schema`. This is critical for deployments that accept parameters (like `tickers` in the `Main` dispatcher).

To ensure compatibility between the Windows host and Linux Docker containers, we use relative entrypoints (e.g., `etl_service.etl.flows.etl.main:main`). This prevents absolute host paths from being captured, which would cause `FileNotFoundError` inside the container.
=======
> **Crucial Implementation Note**: To ensure compatibility between the CI/CD environment (Jenkins) and the execution environment (Docker), we use the modern `flow.deploy()` API.
>
> After registration, we explicitly clear the `pull_steps` and set the `path` to `None` via a server-side `update_deployment()` call. This forces the Prefect worker to use the code already baked into the Docker image, preventing `FileNotFoundError` caused by captured host-specific paths.
>>>>>>> Stashed changes

### 3. Execution Phase
When a flow is triggered, the Prefect worker pulls the specific image. Because the database configuration and application code are already inside the container, execution is fully portable.

## Infrastructure & Networking
For local development using Docker Desktop, containers must be able to resolve both the Prefect server and the host machine.
- **`network_mode`**: We use the `enterprise-network` job variable to ensure all flow containers join the shared Docker network.
- **Host Resolution**: We use `host.docker.internal` to allow containers to talk to the Prefect API and host-mapped database ports.
- **Volume Mounts**: High-volume data (Parquet) is stored on the host (e.g., Google Drive) and mounted into the container at `/data` via the `volumes` job variable.

## Deployment Partitioning
We use the `ENV_PREFIX` variable to logically and physically separate our environments:
- **Naming**: Both flow names and deployment names are prefixed with `{prefix}-` (e.g., `prod-Exchanges-Saver`).
- **Work Pools**:
    - `dev-k8s-pool`: Processes all flows with the `dev-` prefix.
    - `prod-k8s-pool`: Processes all flows with the `prod-` prefix.

## Job Variables & Environment Hardening
To prevent stale metadata from overriding container settings, our `JobVariables` logic explicitly retrieves values from our Pydantic `Settings`.

### Path Portability
On Windows-based development machines, we automatically convert drive letters (e.g., `G:/`) to Docker-friendly paths (e.g., `//g/`) to ensure the Docker worker can mount host directories correctly without validation errors.

## Key Benefits
- **Zero Configuration Leakage**: Dev workers cannot accidentally connect to the Prod database because the connection logic is isolated within the image.
- **Unified Observability**: View all environment runs in a single dashboard while keeping them logically separated.
<<<<<<< Updated upstream
- **Path Portability**: The relative entrypoint strategy ensures that our Windows-based development environment can successfully trigger flows in Linux-based containers.

## Monitoring & Observability
All flows are observable via the Prefect Dashboard.
- **Retries**: Automatically handled by Prefect based on our deployment settings.
- **Logs**: Centralized logging via Loguru, which is integrated with the Prefect UI.
=======
- **Path Portability**: The manual registration fix ensures that our Windows-based development environment can successfully trigger flows in Linux-based containers.
>>>>>>> Stashed changes

## Automated Deployments (CI/CD)
The entire registration process is automated via **Jenkins**:
- **Branch Detection**: PRs automatically register flows with the `dev` prefix.
- **Production Lifecycle**: Merges to `master` trigger the build and registration of `prod` deployments.
- **Self-Healing**: The pipeline ensures work pools exist and deployment metadata is always in sync with the latest container image.

## Deployment Commands
To register all flows with the Prefect server:
```bash
npx nx run etl-service:deploy
```
