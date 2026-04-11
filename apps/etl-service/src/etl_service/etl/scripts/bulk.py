"""Script for saving bulk historical data."""

from datetime import date
import os
from eodhd_client.client import EODHDClientBase
from db_client.client import DBClient
from loguru import logger


def bulk_data_saver(country: str, bus_date: date, data_type: str, run_id: str) -> None:
    """Core logic for saving bulk data."""
    api_key = os.getenv("EODHD_API_KEY")
    client = EODHDClientBase(api_key).bulk
    
    db_client = DBClient(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
    )

    try:
        if data_type == "eod":
            data = client.get_bulk_eod(country=country, date=bus_date.isoformat())
            for item in data:
                db_client.insert_stock_data(
                    bus_date=bus_date,
                    symbol=f"{item['code']}.{country}",
                    open_price=item["open"],
                    high_price=item["high"],
                    low_price=item["low"],
                    close_price=item["close"],
                    adjusted_close_price=item["adjusted_close"],
                    volume=item["volume"]
                )
        elif data_type == "splits":
            data = client.get_bulk_splits(country=country, date=bus_date.isoformat())
            for item in data:
                db_client.insert_stock_splits_data(
                    bus_date=bus_date,
                    symbol=f"{item['code']}.{country}",
                    split=item["split"]
                )
        elif data_type == "dividends":
            data = client.get_bulk_dividends(country=country, date=bus_date.isoformat())
            for item in data:
                db_client.insert_stock_dividends_data(
                    bus_date=bus_date,
                    symbol=f"{item['code']}.{country}",
                    declaration_bus_date=None,  # Not provided in bulk API
                    record_bus_date=None,
                    payment_bus_date=None,
                    period=None,
                    value=item["dividend"],
                    unadjusted_value=item["unadjustedDividend"],
                    currency=None
                )
        logger.info(f"Saved {len(data)} bulk {data_type} records for {country}.")
    except Exception as e:
        logger.error(f"Error saving bulk {data_type} for {country}: {e}")
