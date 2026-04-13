"""Script for saving EOD data."""

import datetime

from loguru import logger

from db_client.client import DBClient
from db_client.models import StockEOD
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings


def eod_saver(bus_date: datetime.date, tickers: list[str], run_id: str) -> None:
    """Core logic for saving End-Of-Day data.

    Args:
        bus_date (datetime.date): The business date.
        tickers (list[str]): List of stock tickers (e.g. ['AAPL.US', 'MSFT.US']).
        run_id (str): Unique identifier for the run.
    """
    client = EODHDClientBase(settings.eodhd_api_key).stocks_etf

    db_client = DBClient(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.effective_db_host,
        port=settings.db_port,
    )

    objects_to_upsert = []
    total_tickers = len(tickers)
    for i, ticker_symbol in enumerate(tickers):
        try:
            # Tickers are expected in 'SYMBOL.EXCHANGE' format
            parts = ticker_symbol.split(".")
            symbol = parts[0]
            exchange = parts[1] if len(parts) > 1 else "US"

            data = client.get_eod_data(
                symbol=symbol,
                exchange=exchange,
                date_from=bus_date.isoformat(),
                date_to=bus_date.isoformat(),
            )

            if data and isinstance(data, list) and len(data) > 0:
                item = data[0]
                obj = StockEOD(
                    bus_date=bus_date,
                    symbol=ticker_symbol,
                    open=item["open"],
                    high=item["high"],
                    low=item["low"],
                    close=item["close"],
                    adjusted_close=item["adjusted_close"],
                    volume=item["volume"],
                )
                objects_to_upsert.append(obj)
                logger.debug(f"Collected EOD data for {ticker_symbol} at {bus_date}")
            else:
                logger.warning(f"No EOD data found for {ticker_symbol} at {bus_date}")

            if (i + 1) % 10 == 0:
                logger.info(
                    f"Progress: {i + 1}/{total_tickers} tickers processed for eod..."
                )

        except Exception as e:
            logger.error(f"Error processing EOD for {ticker_symbol}: {e}")

    if objects_to_upsert:
        success = db_client.bulk_upsert(objects_to_upsert)
        if success:
            logger.info(
                f"Successfully inserted {len(objects_to_upsert)}/{total_tickers} rows into the database."
            )
        else:
            logger.error("Failed to perform bulk upsert for EOD data.")
    else:
        logger.warning("No data collected for bulk upsert.")
