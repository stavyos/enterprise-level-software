# Prefect Orchestrator

Management layer for the Prefect 3.x control plane and Kubernetes execution environment.

## Responsibilities
- **Prefect Server**: Configuration and management of the local or remote Prefect API.
- **Work Pools**: Definition of the Kubernetes work pools where ETL savers are executed.
- **Workers**: Deployment and scaling of Prefect workers within the cluster.

## Key Commands
- **Start All**: `npx nx run prefect-orchestrator:start` (Starts both server and worker).
- **Start Local Server**: `npx nx run prefect-orchestrator:run`
- **Start Local Worker**: `npx nx run prefect-orchestrator:worker`
- **View Dashboard**: Access the Prefect UI (defaults to `http://localhost:4200`) to monitor flow runs and worker status.
