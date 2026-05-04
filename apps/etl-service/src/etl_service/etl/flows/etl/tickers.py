"""Ticker flow module for processing Exchange Symbol List."""

from loguru import logger
from prefect import flow

from db_client.client import DBClient
from db_client.models import Exchange
from etl_service.etl.deployments_settings.deployments.stocks.tickers import (
    DeploymentTickers,
)
from etl_service.etl.deployments_settings.settings import settings
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.tickers import tickers_saver as _tickers_saver

DEPLOYMENT_TICKERS = DeploymentTickers()


@flow(**DEPLOYMENT_TICKERS.saver_flow_decorator_args)
@enable_loguru_support
def tickers_saver(exchange_code: str) -> None:
    """Flow task to save tickers for a specific exchange.

    Args:
        exchange_code (str): The code of the exchange (e.g., 'US').
    """
    logger.info(f"Running ticker saver for exchange={exchange_code}")
    _tickers_saver(exchange_code=exchange_code)


@flow(**DEPLOYMENT_TICKERS.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def tickers_saver_dispatcher(
    exchange_codes: list[str] | None = None,
) -> None:
    """Orchestrates ticker saving for multiple exchanges.

    Args:
        exchange_codes (list[str] | None): List of exchange codes to process.
    """
    if not exchange_codes:
        db_client = DBClient(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.effective_db_host,
            port=settings.db_port,
        )
        with db_client._session() as session:
            exchanges = session.query(Exchange.code).all()
            exchange_codes = [ex[0] for ex in exchanges]

        if not exchange_codes:
            logger.warning(
                "No exchange codes found in the database. Disaptcher will not dispatch sub-flows."
            )
            return

    logger.info(f"Running ticker dispatcher for exchanges={exchange_codes}")

    params_list = [{"exchange_code": code} for code in exchange_codes]

    await DEPLOYMENT_TICKERS.dispatch_sub_flows(params=params_list)

    logger.info(f"Ticker dispatcher completed for exchanges={exchange_codes}")
