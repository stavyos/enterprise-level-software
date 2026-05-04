"""Script for saving Ticker data (Exchange Symbol List)."""

from loguru import logger
from sqlalchemy.dialects.postgresql import insert

from db_client.client import DBClient
from db_client.models import Ticker, VirginTicker
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
        virgin_tickers_data = []
        for item in tickers:
            ticker_code = item.get("Code")
            ticker = Ticker(
                code=ticker_code,
                exchange_code=exchange_code,
                name=item.get("Name"),
                country=item.get("Country"),
                currency=item.get("Currency"),
                type=item.get("Type"),
                isin=item.get("Isin"),
            )
            objects_to_upsert.append(ticker)
            if ticker_code:
                virgin_tickers_data.append(
                    {
                        "ticker": ticker_code,
                        "exchange": exchange_code,
                        "first_eod_bus_date": None,
                    }
                )

        success = db_client.bulk_upsert(objects_to_upsert)
        if success:
            logger.info(
                f"Successfully inserted {len(objects_to_upsert)}/{len(tickers)} tickers for {exchange_code}."
            )

            if virgin_tickers_data:
                with db_client._session() as session:
                    try:
                        stmt = insert(VirginTicker).values(virgin_tickers_data)
                        stmt = stmt.on_conflict_do_nothing(
                            index_elements=["ticker", "exchange"]
                        )
                        session.execute(stmt)
                        session.commit()
                        logger.info(
                            f"Successfully processed virgin tickers for {exchange_code}."
                        )
                    except Exception as e:
                        session.rollback()
                        logger.error(
                            f"Error inserting virgin tickers for {exchange_code}: {e}"
                        )
                        raise RuntimeError(
                            f"Failed to insert virgin tickers: {e}"
                        ) from e
        else:
            error_msg = f"Failed to bulk upsert tickers for {exchange_code}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    except Exception as e:
        logger.error(f"Error processing tickers for {exchange_code}: {e}")
        raise
