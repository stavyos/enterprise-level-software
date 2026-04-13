"""Script for saving Exchanges data."""

import datetime

from loguru import logger

from db_client.client import DBClient
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings


def exchanges_saver(bus_date: datetime.date) -> None:
    """Core logic for saving Exchanges data.

    Args:
        bus_date (datetime.date): The business date.
    """
    client = EODHDClientBase(settings.eodhd_api_key).exchanges

    db_client = DBClient(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.effective_db_host,
        port=settings.db_port,
    )

    try:
        exchanges = client.get_supported_exchanges()

        if not exchanges or not isinstance(exchanges, list):
            logger.warning("No exchanges data received from API.")
            return

        rows_inserted = 0
        for item in exchanges:
            success = db_client.insert_exchange_data(
                code=item.get("Code"),
                name=item.get("Name"),
                country=item.get("Country"),
                currency=item.get("Currency"),
                operating_mic=item.get("OperatingMIC"),
                country_iso2=item.get("CountryISO2"),
                country_iso3=item.get("CountryISO3"),
            )
            if success:
                rows_inserted += 1

        logger.info(
            f"Successfully inserted {rows_inserted}/{len(exchanges)} exchanges into the database."
        )

    except Exception as e:
        logger.error(f"Error processing Exchanges: {e}")
