"""Script for saving Ticker data (Exchange Symbol List)."""

from loguru import logger

from db_client.client import DBClient
from db_client.models import Ticker
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings


def tickers_saver(exchange_code: str) -> None:
    """Core logic for saving Ticker data for a specific exchange.

    Args:
        exchange_code (str): The code of the exchange (e.g., 'US', 'LSE').
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
        logger.info(f"Fetching symbols for exchange: {exchange_code}")
        tickers = client.get_traded_tickers(exchange_code=exchange_code)

        if not tickers or not isinstance(tickers, list):
            logger.warning(f"No tickers data received for exchange {exchange_code}.")
            return

        objects_to_upsert = []
        for item in tickers:
            ticker = Ticker(
                code=item.get("Code"),
                exchange_code=exchange_code,
                name=item.get("Name"),
                country=item.get("Country"),
                currency=item.get("Currency"),
                type=item.get("Type"),
                isin=item.get("Isin"),
            )
            objects_to_upsert.append(ticker)

        success = db_client.bulk_upsert(objects_to_upsert)
        if success:
            logger.info(
                f"Successfully inserted {len(objects_to_upsert)}/{len(tickers)} tickers for {exchange_code}."
            )
        else:
            error_msg = f"Failed to bulk upsert tickers for {exchange_code}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    except Exception as e:
        logger.error(f"Error processing tickers for {exchange_code}: {e}")
        raise
