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

**Example**: A 6-year backfill (2020–2026) triggers approximately 20 sub-flows instead of 1,500+, while maintaining full observability and retry-ability for each chunk.

## Reference Data & Discovery Flows
Our system includes dedicated flows for managing the global asset universe.

### 1. Exchange Metadata
The **Exchanges** flow fetches supported global exchanges from EODHD and persists their codes, names, and currencies. This acts as the foundation for all other discovery tasks.

### 2. Ticker Discovery
The **Tickers** flow utilizes a Dispatcher/Saver pattern to discover symbols for specific exchange codes:
- **Dispatcher**: Takes a list of exchange codes (e.g., `["US", "LSE"]`).
- **Saver**: Fetches every traded ticker for a single exchange and performs a high-performance bulk upsert into the `tickers` table.

This automated discovery ensures that new IPOs and exchange listings are automatically integrated into the system without manual intervention.

The entire registration process is automated via **Jenkins**:
- **Branch Detection**: PRs automatically register flows with the `dev` prefix.
- **Production Lifecycle**: Merges to `master` trigger the build and registration of `prod` deployments.
- **Self-Healing**: The pipeline ensures work pools exist and deployment metadata is always in sync with the latest container image.
