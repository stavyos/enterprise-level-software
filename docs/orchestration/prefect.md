# Workflow Orchestration Strategy

Our system uses a two-tier architecture (Dispatcher/Saver) to handle high-volume financial data acquisition.

## The Image-Baking Pattern
To maintain environment isolation within a single cluster, we use the **Image-Baking** pattern.

### 1. Build Phase
We use Docker build arguments (`--build-arg`) to inject environment-specific database credentials and prefixes into the image.
- `etl-service:dev`: Hardcoded to Port 5434.
- `etl-service:prod`: Hardcoded to Port 5435.

### 2. Registration Phase
When we run the deployment script, we pass the image name. Prefect creates a deployment entry that links the flow to that specific image.

### 3. Execution Phase
When a flow is triggered, the Prefect worker pulls the specific image. Because the database connection string is already inside the container, the worker automatically connects to the correct data instance without needing external environment variables.

## Deployment Suffixes
We use the `ENV_PREFIX` variable to name our deployments:
- `dev`: `Flow-Name/dev`
- `prod`: `Flow-Name/prod`

## Key Benefits
- **Zero Configuration Leakage**: Dev workers cannot accidentally connect to the Prod database because the connection logic is isolated within the image.
- **Unified Observability**: View all environment runs in a single dashboard while keeping them logically separated.
- **Resource Efficiency**: No need to run multiple heavy Prefect control planes locally.
