"""Script for saving bulk historical data."""

from datetime import date

from loguru import logger

from db_client.client import DBClient
from db_client.models import (
    StockDividends,
    StockEOD,
    StockSplits,
)
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings


def bulk_data_saver(country: str, bus_date: date, data_type: str, run_id: str) -> None:
    """Core logic for saving bulk data."""
    client = EODHDClientBase(settings.eodhd_api_key).bulk

    db_client = DBClient(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.effective_db_host,
        port=settings.db_port,
    )

    try:
        objects_to_upsert = []
        if data_type == "eod":
            data = client.get_bulk_eod(country=country, date=bus_date.isoformat())
            total_count = len(data)
            for item in data:
                stock_eod = StockEOD(
                    bus_date=bus_date,
                    symbol=f"{item.get('code')}.{country}",
                    open=item.get("open"),
                    high=item.get("high"),
                    low=item.get("low"),
                    close=item.get("close"),
                    adjusted_close=item.get("adjusted_close"),
                    volume=item.get("volume"),
                )
                objects_to_upsert.append(stock_eod)

        elif data_type == "splits":
            data = client.get_bulk_splits(country=country, date=bus_date.isoformat())
            total_count = len(data)
            for item in data:
                stock_splits = StockSplits(
                    bus_date=bus_date,
                    symbol=f"{item.get('code')}.{country}",
                    split=item.get("split"),
                )
                objects_to_upsert.append(stock_splits)

        elif data_type == "dividends":
            data = client.get_bulk_dividends(country=country, date=bus_date.isoformat())
            total_count = len(data)
            for item in data:
                stock_dividends = StockDividends(
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
                objects_to_upsert.append(stock_dividends)

        success = db_client.bulk_upsert(objects_to_upsert)
        if success:
            logger.info(
                f"Finished: {len(objects_to_upsert)}/{total_count} bulk {data_type} records saved for {country}."
            )
        else:
            logger.error(f"Failed to bulk upsert {data_type} for {country}")

    except Exception as e:
        logger.error(f"Error saving bulk {data_type} for {country}: {e}")
