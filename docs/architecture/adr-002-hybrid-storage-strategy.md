# ADR-002: Hybrid Storage Strategy (TimescaleDB + Parquet)

## Status
Accepted

<<<<<<< Updated upstream
## Date
2026-04-27

## Context
Our system handles various types of financial data, ranging from daily EOD prices to high-frequency intraday data. Intraday data, specifically at the 1-minute interval, generates a massive volume of records that can strain traditional relational databases, even those optimized for time-series like TimescaleDB.

### Constraints
- **Storage Efficiency**: 1-minute intraday data is too voluminous for efficient relational storage at scale.
- **Analytical Performance**: Financial analysts often prefer Parquet files for heavy data processing using tools like Spark, Dask, or DuckDB.
- **Simplicity**: We want to avoid managing multiple variations of the same data (e.g., 5m, 1h intervals) if they can be derived from a base interval.

## Decision
We will implement a **Hybrid Storage Strategy**:
1.  **TimescaleDB**: Will continue to store all "lightweight" data, including EOD prices, dividends, splits, exchanges, and market news.
2.  **Parquet Files**: All 1-minute intraday data will be stored as partitioned Parquet files using `pyarrow`.
3.  **Interval Restriction**: The system will strictly support only the 1-minute interval for intraday data. Higher-level intervals (5m, 1h, etc.) must be calculated downstream from this base data.

### Implementation
- A new `storage-client` library provides an abstract layer for Parquet persistence.
- Data is partitioned by `symbol` and `bus_date` to ensure efficient lookups and manageable file sizes.
- The `eodhd-client` is hardcoded to request `"1m"` intervals, removing the possibility of fetching redundant datasets.

## Consequences

### Positive
- **Scalability**: Parquet files are significantly more efficient for storing and compressing billions of intraday records.
- **Cost Reduction**: Reduced load on the database instance leads to lower resource costs and better stability.
- **Interoperability**: Parquet is a first-class citizen in the modern data engineering ecosystem.

### Negative
- **Data Fragmentation**: Developers must now interact with two different storage layers (SQL for metadata/EOD, Files for Intraday).
- **Manual Downsampling**: Users needing 5-minute or 1-hour data must implement their own aggregation logic.
=======
## Context
As the volume of intraday market data (1-minute intervals) increases, storing billions of rows in a traditional relational database—even one optimized for time-series like TimescaleDB—can lead to significant overhead in terms of storage costs, indexing performance, and backup complexity.

Intraday data is typically "write-once, read-many" and often processed in bulk for analytical purposes (e.g., backtesting, feature engineering).

## Decision
We will adopt a hybrid storage strategy to optimize for both transactional metadata and high-volume analytical data:

1.  **Metadata and EOD Data (TimescaleDB)**:
    -   Exchanges, Tickers, and End-of-Day (EOD) prices will remain in **TimescaleDB**.
    -   These datasets are relatively small and benefit from SQL's relational integrity and complex join capabilities.
2.  **Intraday Data (Parquet)**:
    -   1-minute intraday data will be stored as **partitioned Parquet files**.
    -   Storage will be organized by `symbol` and `bus_date` (e.g., `data/intraday/symbol=AAPL/bus_date=2026-04-24/data.parquet`).
    -   Parquet provides superior compression (Snappy) and column-oriented performance for analytical queries.

## Infrastructure & Portability
To ensure the system remains portable and cloud-ready:
-   **Local Storage**: Data is stored on a host-mounted path (e.g., Google Drive for local development).
-   **Docker Isolation**: Containers mount the host's `DATA_DIR` to an internal `/data` path.
-   **Environment Separation**: Strict isolation between `data/dev` and `data/prd`.

## Consequences
-   **Positive**: Significant reduction in database storage requirements and improved performance for bulk data reads.
-   **Positive**: Lower cost for long-term data archival.
-   **Negative**: Reading intraday data now requires a Parquet-aware client (e.g., `pandas`, `polars`, or `duckdb`) instead of a simple SQL query.
-   **Negative**: Managing file-based consistency (ensuring no partial writes) becomes the responsibility of the application layer (`storage-client`).
>>>>>>> Stashed changes
