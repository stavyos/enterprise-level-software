import pandas as pd
from storage_client.parquet import LocalParquetStorage


def test_save_partitioned(tmp_path):
    storage = LocalParquetStorage(base_path=tmp_path)
    df = pd.DataFrame(
        {
            "timestamp": [1712520000, 1712520060],
            "open": [150.0, 150.1],
            "symbol": ["AAPL", "AAPL"],
            "bus_date": ["2024-04-08", "2024-04-08"],
        }
    )

    success = storage.save_partitioned(df, "test_dataset", ["symbol", "bus_date"])

    assert success is True
    dataset_path = tmp_path / "test_dataset"
    assert dataset_path.exists()

    # Check if partitioning folders exist
    partition_path = dataset_path / "symbol=AAPL" / "bus_date=2024-04-08"
    assert partition_path.exists()

    # Check if parquet file exists in partition
    parquet_files = list(partition_path.glob("*.parquet"))
    assert len(parquet_files) > 0
