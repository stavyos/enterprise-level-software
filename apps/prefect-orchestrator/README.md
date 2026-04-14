# Prefect Orchestrator

Management layer for the Prefect 3.x control plane.

## Key Commands
- **Start All**: `npx nx run prefect-orchestrator:start` (Starts both server and worker).
- **Start Server**: `npx nx run prefect-orchestrator:run`
- **Start Worker**: `npx nx run prefect-orchestrator:worker`
- **View Dashboard**: [http://localhost:4200](http://localhost:4200)

## Architecture
This application manages a **single unified Prefect cluster**. Environment isolation (Dev/Prod) is achieved at the `etl-service` layer through prefixed deployments and isolated Docker images.

## Development
- **Lint**: `npx nx run prefect-orchestrator:lint`
- **Format**: `npx nx run prefect-orchestrator:format`
- **Test**: `npx nx run prefect-orchestrator:test`
