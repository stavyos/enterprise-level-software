"""Script for saving Intraday data."""

import datetime

from loguru import logger
import pandas as pd
from storage_client import LocalParquetStorage

from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings


def intraday_saver(
    tickers: list[str],
    bus_date: datetime.date | None = None,
    start_timestamp: int | None = None,
    end_timestamp: int | None = None,
) -> None:
    """Core logic for saving Intraday data.

    Args:
        tickers (list[str]): List of stock tickers.
        bus_date (datetime.date | None): Single date fetch (legacy support).
        start_timestamp (int | None): Start Unix timestamp for range fetch.
        end_timestamp (int | None): End Unix timestamp for range fetch.
    """
    client = EODHDClientBase(settings.eodhd_api_key).stocks_etf

    parquet_storage = (
        LocalParquetStorage(base_path=settings.data_dir)
        if hasattr(settings, "data_dir")
        else LocalParquetStorage(base_path="data")
    )

    # Determine range
    if start_timestamp and end_timestamp:
        ts_from, ts_to = start_timestamp, end_timestamp
    elif bus_date:
        dt_start = datetime.datetime.combine(bus_date, datetime.time.min)
        dt_end = datetime.datetime.combine(bus_date, datetime.time.max)
        ts_from = int(dt_start.timestamp())
        ts_to = int(dt_end.timestamp())
    else:
        raise ValueError("Either bus_date or start/end timestamps must be provided.")

    total_inserted_count = 0
    failed_tickers = []
    for ticker_symbol in tickers:
        try:
            parts = ticker_symbol.split(".")
            symbol = parts[0]
            exchange = parts[1] if len(parts) > 1 else "US"

            data = client.get_intraday_data(
                symbol=symbol,
                exchange=exchange,
                date_from=ts_from,
                date_to=ts_to,
            )

            if data and isinstance(data, list):
                df = pd.DataFrame(data)

                # Dynamic bus_date extraction from 'datetime' column (e.g. '2026-04-30 15:59:00')
                # This ensures multi-day chunks are partitioned correctly.
                df["symbol"] = ticker_symbol
                df["bus_date"] = pd.to_datetime(df["datetime"]).dt.date.astype(str)

                success = parquet_storage.save_partitioned(
                    df=df,
                    dataset_name="intraday",
                    partition_cols=["symbol", "bus_date"],
                )

                if success:
                    total_inserted_count += len(df)
                    unique_days = df["bus_date"].nunique()
                    logger.info(
                        f"Saved {len(df)} records for {ticker_symbol} spanning {unique_days} days to Parquet."
                    )
                else:
                    logger.error(f"Failed to save Parquet data for {ticker_symbol}")
                    failed_tickers.append(ticker_symbol)
            else:
                logger.warning(
                    f"No intraday data found for {ticker_symbol} in requested range."
                )

        except Exception as e:
            logger.error(f"Error processing Intraday for {ticker_symbol}: {e}")
            failed_tickers.append(ticker_symbol)

    if failed_tickers:
        error_msg = f"Failed to process intraday data for tickers: {failed_tickers}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.info(
        f"Successfully saved {total_inserted_count} total intraday rows to Parquet."
    )
