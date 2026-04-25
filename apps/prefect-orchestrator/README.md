# Prefect Orchestrator

Management layer for the Prefect 3.x control plane.

## Key Commands
- **Start Dev Stack**: `npx nx run prefect-orchestrator:start` (Starts server and dev worker).
- **Start Prod Stack**: `npx nx run prefect-orchestrator:start:prod` (Starts server and prod worker).
- **Start Server**: `npx nx run prefect-orchestrator:run`
- **Start Dev Worker**: `npx nx run prefect-orchestrator:worker`
- **Start Prod Worker**: `npx nx run prefect-orchestrator:worker:prod`
- **View Dashboard**: [http://localhost:4200](http://localhost:4200)

## Architecture
This application manages a **single unified Prefect cluster**. Environment isolation (Dev/Prod) is achieved at the `etl-service` layer through prefixed deployments, isolated Docker images, and separate work pools (`dev-k8s-pool` vs `prod-k8s-pool`).


## CI/CD
The orchestration layer is integrated into the **Jenkins** pipeline:
- **Work Pool Validation**: The pipeline ensures the required environment-specific pools exist before deployment.
- **Server Health**: Monitors the health of the containerized Prefect server on the shared network.

## Development
- **Lint**: `npx nx run prefect-orchestrator:lint`
- **Format**: `npx nx run prefect-orchestrator:format`
- **Test**: `npx nx run prefect-orchestrator:test`
