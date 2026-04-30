# Parquet Data Storage

## Overview
For high-volume 1-minute intraday data, we use **Apache Parquet** as our primary persistence format. This approach complements our **TimescaleDB** instance, creating a hybrid storage architecture optimized for both relational metadata and massive time-series analytical datasets.

## Why Parquet?
1.  **Compression**: Parquet's columnar storage and Snappy compression significantly reduce the storage footprint compared to SQL tables.
2.  **Performance**: analytical queries (e.g., "Give me all AAPL data for 2026") are much faster as they only read the relevant columns and partitions.
3.  **Portability**: Parquet files are self-describing and can be read by a wide range of tools (`pandas`, `duckdb`, `spark`) without requiring a running database server.

## Partitioning Strategy
Data is stored using a standard Hive-style partitioning scheme to enable efficient pruning during reads:

`{DATA_DIR}/intraday/symbol={SYMBOL}/bus_date={YYYY-MM-DD}/{UUID}.parquet`

-   **`symbol`**: The primary partition key.
-   **`bus_date`**: The secondary partition key (Business Date).

## Infrastructure Integration
### Storage Client
We use a custom `storage-client` library (located in `libs/storage-client`) that wraps `pyarrow` and `pandas`.

```python
from storage_client import LocalParquetStorage

storage = LocalParquetStorage(base_path="/data")
storage.save_partitioned(
    df=df,
    dataset_name="intraday",
    partition_cols=["symbol", "bus_date"]
)
```

### Environment Isolation
Data is physically isolated by environment prefixes:
-   **Development**: `G:/My Drive/.../data/dev/intraday`
-   **Production**: `G:/My Drive/.../data/prd/intraday`

### Docker Mounting
In our Prefect orchestration, the host path defined in `DATA_DIR` is automatically mounted to the container's `/data` directory. This allows the ETL code to use a consistent path (`/data`) regardless of whether it is running on a developer's Windows machine or a production Linux server.

## Tools for Reading
-   **Python**: Use `pandas.read_parquet()` or `polars.read_parquet()`.
-   **SQL**: Use **DuckDB** to query Parquet files directly with SQL.
-   **VS Code**: Use the "Parquet Viewer" extension to inspect files visually.
