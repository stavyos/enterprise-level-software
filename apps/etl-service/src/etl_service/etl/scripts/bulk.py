"""Script for saving bulk historical data."""

import os
from datetime import date

from db_client.client import DBClient
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings
from loguru import logger


def bulk_data_saver(country: str, bus_date: date, data_type: str, run_id: str) -> None:
    """Core logic for saving bulk data."""
    client = EODHDClientBase(settings.eodhd_api_key).bulk

    db_client = DBClient(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )

    inserted_count = 0
    try:
        if data_type == "eod":
            data = client.get_bulk_eod(country=country, date=bus_date.isoformat())
            total_count = len(data)
            for i, item in enumerate(data):
                success = db_client.insert_stock_data(
                    bus_date=bus_date,
                    symbol=f"{item.get('code')}.{country}",
                    open_price=item.get("open"),
                    high_price=item.get("high"),
                    low_price=item.get("low"),
                    close_price=item.get("close"),
                    adjusted_close_price=item.get("adjusted_close"),
                    volume=item.get("volume"),
                )
                if success:
                    inserted_count += 1
                
                if (i + 1) % 1000 == 0:
                    logger.info(f"Progress: {i + 1}/{total_count} bulk eod records processed for {country}...")

        elif data_type == "splits":
            data = client.get_bulk_splits(country=country, date=bus_date.isoformat())
            total_count = len(data)
            for i, item in enumerate(data):
                success = db_client.insert_stock_splits_data(
                    bus_date=bus_date, symbol=f"{item.get('code')}.{country}", split=item.get("split")
                )
                if success:
                    inserted_count += 1
                
                if (i + 1) % 100 == 0:
                    logger.info(f"Progress: {i + 1}/{total_count} bulk splits records processed for {country}...")

        elif data_type == "dividends":
            data = client.get_bulk_dividends(country=country, date=bus_date.isoformat())
            total_count = len(data)
            for i, item in enumerate(data):
                success = db_client.insert_stock_dividends_data(
                    bus_date=bus_date,
                    symbol=f"{item.get('code')}.{country}",
                    declaration_bus_date=date.fromisoformat(item["declarationDate"])
                    if item.get("declarationDate")
                    else None,
                    record_bus_date=date.fromisoformat(item["recordDate"])
                    if item.get("recordDate")
                    else None,
                    payment_bus_date=date.fromisoformat(item["paymentDate"])
                    if item.get("paymentDate")
                    else None,
                    period=item.get("period"),
                    value=item.get("value"),
                    unadjusted_value=item.get("unadjustedValue"),
                    currency=item.get("currency"),
                )
                if success:
                    inserted_count += 1
                
                if (i + 1) % 100 == 0:
                    logger.info(f"Progress: {i + 1}/{total_count} bulk dividends records processed for {country}...")
        
        logger.info(f"Finished: {inserted_count}/{total_count} bulk {data_type} records saved for {country}.")
    except Exception as e:
        logger.error(f"Error saving bulk {data_type} for {country}: {e}")
