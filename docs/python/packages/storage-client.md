# Storage Client

The `storage-client` is a internal library designed to handle high-volume financial data persistence using the Parquet format. It complements TimescaleDB by providing a cost-effective and performant way to store intraday historical data.

## Overview

- **Format**: Apache Parquet
- **Compression**: Snappy
- **Library**: `pyarrow` and `pandas`
- **Goal**: Offload high-cardinality intraday data from the relational database to partitioned files.

## Storage Strategy: Hybrid Approach

We use a hybrid storage model to balance query flexibility and storage efficiency:

1.  **TimescaleDB**: Stores metadata (exchanges, tickers) and End-of-Day (EOD) data. This allows for fast SQL queries on daily trends and portfolio metadata.
2.  **Parquet**: Stores 1-minute intraday data. This data is partitioned by `symbol` and `bus_date` to allow for efficient "needle-in-a-haystack" retrieval without bloating the database.

## Partitioning Scheme

Files are stored on the host filesystem (configured via `DATA_DIR`) using Hive-style partitioning:

```text
data/
└── dev/
    └── intraday/
        ├── symbol=AAPL.US/
        │   └── bus_date=2026-04-30/
        │       └── <uuid>-0.parquet
        └── symbol=TSLA.US/
            └── bus_date=2026-04-29/
                └── <uuid>-0.parquet
```

## Usage

```python
from storage_client.parquet import LocalParquetStorage

storage = LocalParquetStorage(base_path="/data")
storage.save_partitioned(
    df=my_dataframe,
    category="intraday",
    partition_cols=["symbol", "bus_date"]
)
```

## Configuration

The storage location is determined by the `DATA_DIR` environment variable. On Windows development machines using Docker, this path is automatically translated from `C:/path` to `//c/path` to ensure compatibility with Docker bind mounts.
