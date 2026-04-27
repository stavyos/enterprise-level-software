# Storage Client

The `storage-client` library provides an abstract and generic layer for file-based data persistence, specifically optimized for Parquet datasets.

## Purpose
In our [Hybrid Storage Strategy](../../architecture/adr-002-hybrid-storage-strategy.md), we use this library to handle high-volume data (like 1-minute intraday prices) that is not suitable for traditional relational databases.

## Key Features

### 1. Abstract Parquet Storage
The `LocalParquetStorage` class abstracts away the complexities of `pyarrow` and `pandas` to provide a simple interface for saving DataFrames.

### 2. Dataset Partitioning
The client supports native Parquet partitioning. By default, our intraday data is partitioned by `symbol` and `bus_date`:
```
data/
├── dev/
│   └── intraday/
│       └── symbol=AAPL/
│           └── bus_date=2026-04-27/
└── prd/
    └── intraday/
        └── symbol=AAPL/
            └── bus_date=2026-04-27/
```
This structure allows for extremely fast data skipping during analytical queries.

### 3. Snappy Compression
All data is automatically compressed using the Snappy algorithm, providing an excellent balance between compression ratio and CPU overhead.

## Usage Example

```python
from storage_client import LocalParquetStorage
import pandas as pd

# Initialize storage at a specific base path
storage = LocalParquetStorage(base_path="data")

# Create some data
df = pd.DataFrame([
    {"timestamp": 1714200000, "price": 150.0, "symbol": "AAPL", "bus_date": "2026-04-27"}
])

# Save as a partitioned dataset
storage.save_partitioned(
    df=df,
    dataset_name="intraday",
    partition_cols=["symbol", "bus_date"]
)
```

## Configuration
The storage path is managed via the `DATA_DIR` environment variable, which is exposed through our central [Pydantic Settings](../../tooling/pydantic-settings.md).
