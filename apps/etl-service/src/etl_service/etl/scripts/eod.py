"""Script for saving EOD data."""

import datetime
import os

from db_client.client import DBClient
from eodhd_client.client import EODHDClientBase
from loguru import logger


def eod_saver(bus_date: datetime.date, tickers: list[str], run_id: str) -> None:
    """Core logic for saving End-Of-Day data.

    Args:
        bus_date (datetime.date): The business date.
        tickers (list[str]): List of stock tickers (e.g. ['AAPL.US', 'MSFT.US']).
        run_id (str): Unique identifier for the run.
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

    for ticker_symbol in tickers:
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
                db_client.insert_stock_data(
                    bus_date=bus_date,
                    symbol=ticker_symbol,
                    open_price=item["open"],
                    high_price=item["high"],
                    low_price=item["low"],
                    close_price=item["close"],
                    adjusted_close_price=item["adjusted_close"],
                    volume=item["volume"],
                )
                logger.info(f"Saved EOD data for {ticker_symbol} at {bus_date}")
            else:
                logger.warning(f"No EOD data found for {ticker_symbol} at {bus_date}")

        except Exception as e:
            logger.error(f"Error processing EOD for {ticker_symbol}: {e}")
