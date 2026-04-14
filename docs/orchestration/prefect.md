# Workflow Orchestration with Prefect 3.x

Our system uses **Prefect 3.x** to manage, schedule, and observe complex ETL pipelines. Prefect allows us to transform local Python functions into distributed, production-ready workflows.

## Environment Separation

We maintain strict isolation between **Development** and **Production** orchestration layers.

| Environment | UI Port | Work Pool | Database Port |
| :--- | :--- | :--- | :--- |
| **Development** | `4200` | `dev-k8s-pool` | `5434` |
| **Production** | `4201` | `prod-k8s-pool` | `5435` |

## The Dispatcher/Saver Pattern

To handle enterprise-scale data (e.g., fetching 20 years of intraday data for 5,000 tickers), we use a two-tier architecture:

### 1. The Dispatcher Flow
The Dispatcher accepts high-level parameters, splits the workload into smaller "chunks", and dispatches multiple parallel **Saver** flow runs.

### 2. The Saver Flow
The Saver executes the actual API calls for a small chunk of data and persists the data to TimescaleDB.

## Configuration Management

We use **Prefect Profiles** combined with **`python-dotenv`** to manage environment-specific configurations.

- **Dev Profile**: Connected to `http://127.0.0.1:4200/api`.
- **Prod Profile**: Connected to `http://127.0.0.1:4201/api`.

### Automatic Variable Loading
Our Nx targets use `dotenv` to load the correct `.env.dev` or `.env.prod` file before executing any Prefect command.

## Kubernetes Integration

All flows are registered as **Deployments** using the Prefect Kubernetes worker model.

### Job Variables
We define resource requirements in `deployments_settings/`. This allows us to scale savers horizontally:
- **CPU Request**: Ensuring enough compute for data processing.
- **Memory Request**: Tailored to the specific data type.

## Deployment Commands

### Development (Dev)
To register all flows with the Dev Prefect server:
```bash
npx nx run etl-service:deploy:dev
```

### Production (Prod)
To register all flows with the Prod Prefect server:
```bash
npx nx run etl-service:deploy:prod
```
