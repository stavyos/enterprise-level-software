# Workflow Orchestration Strategy

Our system uses a two-tier architecture (Dispatcher/Saver) to handle high-volume financial data acquisition.

## The Image-Baking Pattern
To maintain environment isolation within a single cluster, we use the **Image-Baking** pattern.

### 1. Build Phase
We use Docker build arguments (`--build-arg`) to inject environment-specific database credentials and prefixes into the image.
- `etl-service:dev`: Baked with Port 5434.
- `etl-service:prod`: Baked with Port 5435.

### 2. Registration Phase (Portable Strategy)
Deployment registration is handled in `apps/etl-service/src/etl_service/etl/deploy_etls.py`. We use a **Portable Deployment Strategy** to ensure flows registered from a development machine (Windows) work perfectly in production environments (Linux).

1.  **`flow.deploy(build=False)`**: We use the modern Prefect `flow.deploy` API. By setting `build=False`, we prevent Prefect from attempting to rebuild the image or pull code from the local filesystem.
2.  **Post-Registration Update**: After the deployment is registered, we explicitly clear the `path` and `pull_steps` attributes using the Prefect Client. This forces the worker to use the code **already baked into the container image** at the `PYTHONPATH` location, effectively making the deployment environment-agnostic.

### Job Variables & Infrastructure Hardening
Our `JobVariables` logic ensures that infrastructure-specific configuration (like Docker volumes) is correctly applied:
- **Volume Translation**: Automatically converts Windows drive paths (e.g., `C:/path`) to Docker-compatible forward-slash paths (`//c/path`).
- **Network Isolation**: Forces all ETL containers onto the `enterprise-network` to allow resolution of `host.docker.internal` for database access.
### Backfill & Date Range Strategy

The Intraday Dispatcher supports orchestrated backfills via the `end_date` parameter:

1.  **Calendar-Day Chunking**: To maximize API efficiency, the dispatcher automatically splits date ranges into **120-calendar-day chunks** (the maximum allowed by EODHD for 1-minute data).
2.  **Optimized Dispatching**: Instead of one sub-flow per day, the system dispatches one sub-flow per 120-day chunk per ticker. This reduces Prefect overhead by ~98% for long-range backfills.
3.  **Dynamic Partitioning**: The `intraday_saver` dynamically extracts the `bus_date` from the retrieved records, ensuring that a single multi-day API response is correctly partitioned into daily Parquet files in the storage layer.

### Historical Persistence (EOD)
For daily stock data (EOD), the system is optimized for full historical retrieval:
- **Default Start Date**: Dispatchers for EOD and News default to `1900-01-01` to ensure comprehensive backfills for all symbols.
- **Volume Handling**: The storage layer uses `BigInteger` for EOD data to accommodate the massive lifetime volume of high-cap tickers (e.g., AAPL).

### Reference Flow Policy
Reference data flows (Metadata, Exchanges, Symbols) follow a "Current State" pattern:
- **Parameter Minimalization**: These flows do not accept date parameters (e.g., `bus_date`) because the source APIs provide only the current global state.
- **Consistency**: Removing these parameters prevents misleading UI options and ensures that a manual run always fetches the latest truth from the API.

The entire registration process is automated via **Jenkins**:
- **Branch Detection**: PRs automatically register flows with the `dev` prefix.
- **Production Lifecycle**: Merges to `master` trigger the build and registration of `prod` deployments.
- **Self-Healing**: The pipeline ensures work pools exist and deployment metadata is always in sync with the latest container image.
