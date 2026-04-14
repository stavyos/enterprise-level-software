# Prefect Orchestrator

Management layer for the Prefect 3.x control plane and Kubernetes execution environment.

## Responsibilities
- **Prefect Server**: Configuration and management of the local or remote Prefect API.
- **Work Pools**: Definition of the Kubernetes work pools where ETL savers are executed.
- **Workers**: Deployment and scaling of Prefect workers within the cluster.

## Key Commands

| Task | Development (Dev) | Production (Prod) |
| :--- | :--- | :--- |
| **Start All** | `npx nx run prefect-orchestrator:start:dev` | `npx nx run prefect-orchestrator:start:prod` |
| **Start Server** | `npx nx run prefect-orchestrator:run:dev` | `npx nx run prefect-orchestrator:run:prod` |
| **Start Worker** | `npx nx run prefect-orchestrator:worker:dev` | `npx nx run prefect-orchestrator:worker:prod` |
| **UI URL** | `http://localhost:4200` | `http://localhost:4201` |

## Environment Configuration
This application uses `python-dotenv` to manage environment-specific configurations.
- Use `.env.dev` for development.
- Use `.env.prod` for production.

To run a single command with specific environment:
```bash
uv run dotenv -f ../../.env.prod run -- prefect server start
```

## Development

This project follows the monorepo's unified linting and formatting standards using **Ruff**.

- **Lint**: `npx nx run prefect-orchestrator:lint`
- **Format**: `npx nx run prefect-orchestrator:format`
- **Test**: `npx nx run prefect-orchestrator:test`
