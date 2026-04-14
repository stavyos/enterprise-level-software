"""Script for saving Exchanges data."""

import datetime

from loguru import logger

from db_client.client import DBClient
from db_client.models import Exchange
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

        objects_to_upsert = []
        for item in exchanges:
            exchange = Exchange(
                code=item.get("Code"),
                name=item.get("Name"),
                country=item.get("Country"),
                currency=item.get("Currency"),
                operating_mic=item.get("OperatingMIC"),
                country_iso2=item.get("CountryISO2"),
                country_iso3=item.get("CountryISO3"),
            )
            objects_to_upsert.append(exchange)

        success = db_client.bulk_upsert(objects_to_upsert)
        if success:
            logger.info(
                f"Successfully inserted {len(objects_to_upsert)}/{len(exchanges)} exchanges into the database."
            )
        else:
            logger.error("Failed to bulk upsert exchanges data")

    except Exception as e:
        logger.error(f"Error processing Exchanges: {e}")
