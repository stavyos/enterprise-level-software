# Workflow Orchestration with Prefect 3.x

Our system uses **Prefect 3.x** to manage, schedule, and observe complex ETL pipelines.

## Environment Separation

We maintain isolation between **Development** and **Production** using a single cluster with prefixed deployments and isolated databases.

| Feature | Shared Value |
| :--- | :--- |
| **API URL** | `http://127.0.0.1:4200/api` |
| **Work Pool** | `my-k8s-pool` |

### Deployment Prefixing
To distinguish between environments, we use the `ENV_PREFIX` variable:
- **Dev Flows**: Prefixed with `dev-` (e.g., `dev-EOD-Saver`).
- **Prod Flows**: Prefixed with `prod-` (e.g., `prod-EOD-Saver`).

## The Dispatcher/Saver Pattern
To handle enterprise-scale data, we use a two-tier architecture:
1.  **The Dispatcher Flow**: Splits the workload into smaller "chunks".
2.  **The Saver Flow**: Executes the actual API calls and persists data to the isolated environment database.

## Deployment Commands

### Development (Dev)
To register all flows with `dev-` prefix:
```bash
npx nx run etl-service:deploy:dev
```

### Production (Prod)
To register all flows with `prod-` prefix:
```bash
npx nx run etl-service:deploy:prod
```
