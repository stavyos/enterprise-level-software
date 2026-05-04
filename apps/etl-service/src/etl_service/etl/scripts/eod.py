"""Script for saving EOD data."""

import datetime

from loguru import logger
from sqlalchemy import update

from db_client.client import DBClient
from db_client.models import StockEOD, VirginTicker
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings


def eod_saver(bus_date: datetime.date | None, tickers: list[str], run_id: str) -> None:
    """Core logic for saving End-Of-Day data.

    Args:
        bus_date (datetime.date): The business date.
        tickers (list[str]): List of stock tickers (e.g. ['AAPL.US', 'MSFT.US']).
        run_id (str): Unique identifier for the run.
    """
    client = EODHDClientBase(settings.eodhd_api_key).stocks_etf

    db_client = DBClient(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.effective_db_host,
        port=settings.db_port,
    )

    objects_to_upsert = []
    total_tickers = len(tickers)
    failed_tickers = []
    virgin_updates = []
    for i, ticker_symbol in enumerate(tickers):
        try:
            # Tickers are expected in 'SYMBOL.EXCHANGE' format
            parts = ticker_symbol.split(".")
            symbol = parts[0]
            exchange = parts[1] if len(parts) > 1 else "US"

            date_from_str = bus_date.isoformat() if bus_date else None
            date_to_str = bus_date.isoformat() if bus_date else None

            data = client.get_eod_data(
                symbol=symbol,
                exchange=exchange,
                date_from=date_from_str,
                date_to=date_to_str,
            )

            if data and isinstance(data, list) and len(data) > 0:
                min_date_str = None
                for item in data:
                    item_date_str = item.get("date")
                    if not item_date_str and bus_date:
                        item_date_str = bus_date.isoformat()

                    if item_date_str:
                        if not min_date_str or item_date_str < min_date_str:
                            min_date_str = item_date_str
                        item_date = datetime.date.fromisoformat(item_date_str)
                        obj = StockEOD(
                            bus_date=item_date,
                            symbol=ticker_symbol,
                            open=item.get("open"),
                            high=item.get("high"),
                            low=item.get("low"),
                            close=item.get("close"),
                            adjusted_close=item.get("adjusted_close"),
                            volume=item.get("volume"),
                        )
                        objects_to_upsert.append(obj)

                if bus_date is None:
                    first_eod = (
                        datetime.date.fromisoformat(min_date_str)
                        if min_date_str
                        else datetime.date(1900, 1, 1)
                    )
                    virgin_updates.append(
                        {
                            "ticker": symbol,
                            "exchange": exchange,
                            "first_eod_bus_date": first_eod,
                        }
                    )
                logger.debug(f"Collected EOD data for {ticker_symbol}")
            else:
                logger.warning(f"No EOD data found for {ticker_symbol}")
                if bus_date is None:
                    virgin_updates.append(
                        {
                            "ticker": symbol,
                            "exchange": exchange,
                            "first_eod_bus_date": datetime.date(1900, 1, 1),
                        }
                    )

            if (i + 1) % 10 == 0:
                logger.info(
                    f"Progress: {i + 1}/{total_tickers} tickers processed for eod..."
                )

        except Exception as e:
            logger.error(f"Error processing EOD for {ticker_symbol}: {e}")
            failed_tickers.append(ticker_symbol)

    if failed_tickers:
        error_msg = f"Failed to process EOD data for tickers: {failed_tickers}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    if objects_to_upsert:
        success = db_client.bulk_upsert(objects_to_upsert)
        if success:
            logger.info(
                f"Successfully inserted {len(objects_to_upsert)} rows into the database."
            )

            if bus_date is None and virgin_updates:
                with db_client._session() as session:
                    try:
                        for vu in virgin_updates:
                            stmt = (
                                update(VirginTicker)
                                .where(
                                    VirginTicker.ticker == vu["ticker"],
                                    VirginTicker.exchange == vu["exchange"],
                                )
                                .values(first_eod_bus_date=vu["first_eod_bus_date"])
                            )
                            session.execute(stmt)
                        session.commit()
                        logger.info("Successfully updated virgin tickers.")
                    except Exception as e:
                        session.rollback()
                        logger.error(f"Error updating virgin tickers: {e}")
                        raise RuntimeError(
                            f"Failed to update virgin tickers: {e}"
                        ) from e

        else:
            error_msg = "Failed to perform bulk upsert for EOD data."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
    else:
        logger.warning("No data collected for bulk upsert.")
        if bus_date is None and virgin_updates:
            with db_client._session() as session:
                try:
                    for vu in virgin_updates:
                        stmt = (
                            update(VirginTicker)
                            .where(
                                VirginTicker.ticker == vu["ticker"],
                                VirginTicker.exchange == vu["exchange"],
                            )
                            .values(first_eod_bus_date=vu["first_eod_bus_date"])
                        )
                        session.execute(stmt)
                    session.commit()
                    logger.info(
                        "Successfully updated virgin tickers (no data found for any)."
                    )
                except Exception as e:
                    session.rollback()
                    logger.error(f"Error updating virgin tickers: {e}")
                    raise RuntimeError(f"Failed to update virgin tickers: {e}") from e
