"""Script for saving Intraday data."""

import datetime
import os

from db_client.client import DBClient
from eodhd_client.client import EODHDClientBase
from loguru import logger


def intraday_saver(bus_date: datetime.date, tickers: list[str], interval: str = "1m") -> None:
    """Core logic for saving Intraday data.

    Args:
        bus_date (datetime.date): The business date.
        tickers (list[str]): List of stock tickers.
        interval (str): Time interval (e.g. '1m', '5m', '1h').
    """
    api_key = os.getenv("EODHD_API_KEY")
    client = EODHDClientBase(api_key).stocks_etf

    db_client = DBClient(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
    )

    # Convert bus_date to timestamps for EODHD API
    dt_start = datetime.datetime.combine(bus_date, datetime.time.min)
    dt_end = datetime.datetime.combine(bus_date, datetime.time.max)

    timestamp_from = int(dt_start.timestamp())
    timestamp_to = int(dt_end.timestamp())

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
                for item in data:
                    db_client.insert_stock_intraday_data(
                        timestamp=item["timestamp"],
                        symbol=ticker_symbol,
                        bus_date=bus_date,
                        gmt_offset=item["gmtoffset"],
                        open_price=item["open"],
                        high_price=item["high"],
                        low_price=item["low"],
                        close_price=item["close"],
                        volume=item["volume"],
                    )
                logger.info(f"Saved {len(data)} intraday records for {ticker_symbol} at {bus_date}")
            else:
                logger.warning(f"No intraday data found for {ticker_symbol} at {bus_date}")

        except Exception as e:
            logger.error(f"Error processing Intraday for {ticker_symbol}: {e}")
