# ETL Service

The core data acquisition and processing engine powered by Prefect 3.x.

## Environment Isolation: Baked-in Configuration
To ensure absolute data isolation within a shared Prefect cluster, we use environment-specific Docker images and partitioned work pools.

1.  **Build Phase**: Configuration (DB host, port, credentials) is baked into the image using `--build-arg`.
2.  **Registration Phase**:
    *   **Dev**: Deployments are prefixed with `dev-` and assigned to `dev-k8s-pool`.
    *   **Prod**: Deployments are prefixed with `prod-` and assigned to `prod-k8s-pool`.
3.  **Execution Phase**: When a worker runs `etl-service:prod`, it automatically connects to the production database without requiring external environment variables.
## Key Commands

| Task | Development (Dev) | Production (Prod) |
| :--- | :--- | :--- |
| **Build Image** | `npx nx run etl-service:docker-build:dev` | `npx nx run etl-service:docker-build:prod` |
| **Register Flows** | `npx nx run etl-service:deploy:dev` | `npx nx run etl-service:deploy:prod` |

## Development

This project follows the monorepo's unified linting and formatting standards using **Ruff**.

- **Lint**: `npx nx run etl-service:lint`
- **Format**: `npx nx run etl-service:format`
- **Test**: `npx nx run etl-service:test`
