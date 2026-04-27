"""Script for saving Intraday data."""

import datetime

from loguru import logger
import pandas as pd
from storage_client import LocalParquetStorage

from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings


def intraday_saver(bus_date: datetime.date, tickers: list[str]) -> None:
    """Core logic for saving Intraday data.

    Args:
        bus_date (datetime.date): The business date.
        tickers (list[str]): List of stock tickers.
    """
    client = EODHDClientBase(settings.eodhd_api_key).stocks_etf

    parquet_storage = (
        LocalParquetStorage(base_path=settings.data_dir)
        if hasattr(settings, "data_dir")
        else LocalParquetStorage(base_path="data")
    )

    # Convert bus_date to timestamps for EODHD API
    dt_start = datetime.datetime.combine(bus_date, datetime.time.min)
    dt_end = datetime.datetime.combine(bus_date, datetime.time.max)

    timestamp_from = int(dt_start.timestamp())
    timestamp_to = int(dt_end.timestamp())

    total_inserted_count = 0
    for ticker_symbol in tickers:
        try:
            parts = ticker_symbol.split(".")
            symbol = parts[0]
            exchange = parts[1] if len(parts) > 1 else "US"

            data = client.get_intraday_data(
                symbol=symbol,
                exchange=exchange,
                date_from=timestamp_from,
                date_to=timestamp_to,
            )

            if data and isinstance(data, list):
                # Add symbol and bus_date to data for partitioning
                for item in data:
                    item["symbol"] = ticker_symbol
                    item["bus_date"] = str(bus_date)

                df = pd.DataFrame(data)
                success = parquet_storage.save_partitioned(
                    df=df,
                    dataset_name="intraday",
                    partition_cols=["symbol", "bus_date"],
                )

                if success:
                    total_inserted_count += len(df)
                    logger.info(
                        f"Saved {len(df)} records for {ticker_symbol} at {bus_date} to Parquet"
                    )
                else:
                    logger.error(f"Failed to save Parquet data for {ticker_symbol}")
            else:
                logger.warning(
                    f"No intraday data found for {ticker_symbol} at {bus_date}"
                )

        except Exception as e:
            logger.error(f"Error processing Intraday for {ticker_symbol}: {e}")

    logger.info(f"Successfully saved {total_inserted_count} intraday rows to Parquet.")
