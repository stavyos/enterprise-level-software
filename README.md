# Enterprise Level Software

A robust, enterprise-grade financial data acquisition and processing system built with Python, Prefect, and TimescaleDB.

## Project Structure

This workspace is managed using [Nx](https://nx.dev) and is organized into applications and libraries.

### Apps (`apps/`)
- **`etl-service`**: Core ETL logic and Prefect flows for financial data acquisition.
- **`prefect-orchestrator`**: Management of the Prefect control plane.

### Libs (`libs/`)
- **`eodhd-client`**: High-performance, rate-limited Python client for the EODHD API.
- **`db-client`**: Database persistence layer using SQLAlchemy and TimescaleDB.

## Environment Isolation Strategy

We use a **unified Prefect cluster** with strictly isolated data layers:
1.  **Isolated Databases**: Separate TimescaleDB containers for Dev (port 5434) and Prod (port 5435).
2.  **Isolated Images**: Environment-specific Docker images (`etl-service:dev` and `etl-service:prod`) with baked-in configuration.
3.  **Deployment Partitioning**:
    *   **Dev**: Registered with `dev-` prefix in `dev-k8s-pool`.
    *   **Prod**: Registered with `prod-` prefix in `prod-k8s-pool`.

## Getting Started

### Prerequisites
- Docker Desktop (with Kubernetes enabled)
- [uv](https://github.com/astral-sh/uv)
- Node.js (for Nx)

### Configuration
1.  Copy `template.dev.env` to `dev.env` and `template.prod.env` to `prod.env`.
2.  Fill in your `EODHD_API_KEY` and database credentials.

### Infrastructure Setup
```bash
# Start isolated databases
docker-compose up -d

# Start Prefect Cluster with Dev Worker
npx nx run prefect-orchestrator:start

# Start Prefect Cluster with Prod Worker
npx nx run prefect-orchestrator:start:prod
```

### Key Commands

| Task | Development (Dev) | Production (Prod) |
| :--- | :--- | :--- |
| **Docker Build** | `npx nx run etl-service:docker-build:dev` | `npx nx run etl-service:docker-build:prod` |
| **Register Flows** | `npx nx run etl-service:deploy:dev` | `npx nx run etl-service:deploy:prod` |
| **Run Worker** | `npx nx run prefect-orchestrator:worker` | `npx nx run prefect-orchestrator:worker:prod` |
| **Run Tests** | `npx nx run-many -t test` | `npx nx run-many -t test` |

### Triggering Flows
You can trigger flows via the Prefect UI or the CLI. When using the CLI, ensure you use the correct quoting for array parameters:

```bash
# Example: Triggering the Main Dispatcher for AAPL and MSFT in Dev
uv run prefect deployment run "dev-Main-Saver Dispatcher/dev-main-saver dispatcher-deployment" --param 'tickers=["AAPL","MSFT"]'
```

## Documentation
For detailed architecture and setup guides, visit the [Tech Learning Center](docs/index.md).
