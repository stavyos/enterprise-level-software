# ADR-002: Hybrid Storage Strategy (TimescaleDB + Parquet)

## Status
Accepted

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
