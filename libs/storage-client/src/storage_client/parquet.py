from pathlib import Path

from loguru import logger
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


class LocalParquetStorage:
    """Abstract file storage client for saving data to Parquet files locally or on a mounted volume."""

    def __init__(self, base_path: str | Path):
        """Initializes the LocalParquetStorage.

        Args:
            base_path (str | Path): The base directory for storing files.
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"LocalParquetStorage initialized at {self.base_path}")

    def save_partitioned(
        self, df: pd.DataFrame, dataset_name: str, partition_cols: list[str]
    ) -> bool:
        """Saves a DataFrame as a partitioned Parquet dataset.

        Args:
            df (pd.DataFrame): The data to save.
            dataset_name (str): The name of the dataset (e.g., 'intraday').
            partition_cols (list[str]): Columns to partition by (e.g., ['symbol', 'bus_date']).

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            if df.empty:
                logger.warning(
                    f"DataFrame for dataset '{dataset_name}' is empty. Nothing to save."
                )
                return False

            dataset_path = self.base_path / dataset_name

            table = pa.Table.from_pandas(df)
            pq.write_to_dataset(
                table,
                root_path=str(dataset_path),
                partition_cols=partition_cols,
                use_dictionary=True,
                compression="snappy",
            )
            logger.info(
                f"Successfully saved data to {dataset_path} partitioned by {partition_cols}"
            )
            return True
        except Exception as e:
            logger.error(f"Error saving data to parquet: {e}")
            return False
