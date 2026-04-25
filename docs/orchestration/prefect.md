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

> **Crucial Implementation Note**: To ensure compatibility between a Windows host and a Linux Docker container, we use the `RunnerDeployment` constructor directly rather than `from_entrypoint()`. This allows us to manually specify the `entrypoint` and set `path="/app"`. Failure to do this causes Prefect to capture absolute Windows host paths, which leads to `FileNotFoundError` inside the container.

### 3. Execution Phase
When a flow is triggered, the Prefect worker pulls the specific image. Because the database configuration is already inside the container (baked into environment variables), the worker automatically connects to the correct database instance.

## Deployment Partitioning
We use the `ENV_PREFIX` variable to logically and physically separate our environments:
- **Naming**: Both flow names and deployment names are prefixed with `{prefix}-` (e.g., `prod-Exchanges-Saver`).
- **Work Pools**:
    - `dev-k8s-pool`: Processes all flows with the `dev-` prefix.
    - `prod-k8s-pool`: Processes all flows with the `prod-` prefix.

## Job Variables & Environment Hardening
To prevent stale metadata from overriding container settings, our `JobVariables` logic explicitly retrieves values from our Pydantic `Settings`. We call `settings.reload()` during the deployment entry point to ensure that the variables stored on the Prefect server (and subsequently passed to the worker) match the current environment (dev vs. prod).

## Key Benefits
- **Zero Configuration Leakage**: Dev workers cannot accidentally connect to the Prod database because the connection logic is isolated within the image.
- **Unified Observability**: View all environment runs in a single dashboard while keeping them logically separated.
- **Path Portability**: The manual `RunnerDeployment` fix ensures that our Windows-based development environment can successfully trigger flows in Linux-based containers.
