# Workflow Orchestration with Prefect 3.x

Our system uses **Prefect 3.x** to manage, schedule, and observe complex ETL pipelines. Prefect allows us to transform local Python functions into distributed, production-ready workflows.

## The Dispatcher/Saver Pattern

To handle enterprise-scale data (e.g., fetching 20 years of intraday data for 5,000 tickers), we use a two-tier architecture:

### 1. The Dispatcher Flow
The Dispatcher is the entry point. Its responsibility is to:
- Accept high-level parameters (e.g., a list of 500 tickers).
- Split the workload into smaller "chunks".
- Dispatch multiple parallel **Saver** flow runs.

### 2. The Saver Flow
The Saver is a focused worker job that:
- Executes the actual API calls for a small chunk of data.
- Persists the data to TimescaleDB.
- Handles retries and failures locally for its specific chunk.

**Why this pattern?**
- **Parallelism**: Multiple savers can run simultaneously on different Kubernetes nodes.
- **Resilience**: If one saver fails, only its specific chunk needs to be retried, not the entire 500-ticker request.
- **Resource Management**: Each saver can request specific CPU/Memory, preventing memory overflows in the dispatcher.

## Kubernetes Integration

All flows are registered as **Deployments** using the Prefect Kubernetes worker model.

### Job Variables
We define resource requirements in `deployments_settings/`. This allows us to scale savers horizontally:
- **CPU Request**: Ensuring enough compute for data processing.
- **Memory Request**: Tailored to the specific data type (e.g., Fundamentals require more memory than EOD).

## Monitoring & Observability
All flows are observable via the Prefect Dashboard.
- **Retries**: Automatically handled by Prefect based on our deployment settings.
- **Logs**: Centralized logging via Loguru, which is integrated with the Prefect UI.

## Deployment Commands
To register all flows with the Prefect server:
```bash
npx nx run etl-service:deploy
```
