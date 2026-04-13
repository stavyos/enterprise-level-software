"""Script for saving Intraday data."""

import datetime

from loguru import logger

from db_client.client import DBClient
from db_client.models import StockIntraday
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings


def intraday_saver(
    bus_date: datetime.date, tickers: list[str], interval: str = "1m"
) -> None:
    """Core logic for saving Intraday data.

    Args:
        bus_date (datetime.date): The business date.
        tickers (list[str]): List of stock tickers.
        interval (str): Time interval (e.g. '1m', '5m', '1h').
    """
    client = EODHDClientBase(settings.eodhd_api_key).stocks_etf

    db_client = DBClient(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.effective_db_host,
        port=settings.db_port,
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
                interval=interval,
                date_from=timestamp_from,
                date_to=timestamp_to,
            )

            if data and isinstance(data, list):
                objects_to_upsert = []
                for item in data:
                    stock_intraday = StockIntraday(
                        timestamp=item.get("timestamp"),
                        symbol=ticker_symbol,
                        bus_date=bus_date,
                        gmt_offset=item.get("gmtoffset"),
                        open=item.get("open"),
                        high=item.get("high"),
                        low=item.get("low"),
                        close=item.get("close"),
                        volume=item.get("volume"),
                    )
                    objects_to_upsert.append(stock_intraday)

                success = db_client.bulk_upsert(objects_to_upsert)
                if success:
                    total_inserted_count += len(objects_to_upsert)
                    logger.info(
                        f"Saved {len(objects_to_upsert)} records for {ticker_symbol} at {bus_date}"
                    )
                else:
                    logger.error(f"Failed to bulk upsert data for {ticker_symbol}")
            else:
                logger.warning(
                    f"No intraday data found for {ticker_symbol} at {bus_date}"
                )

        except Exception as e:
            logger.error(f"Error processing Intraday for {ticker_symbol}: {e}")

    logger.info(
        f"Successfully inserted {total_inserted_count} intraday rows into the database."
    )
