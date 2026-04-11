"""Intraday ETL flow module."""

import datetime

from loguru import logger
from prefect import flow

from etl_service.etl.deployments_settings.deployments.stocks.intraday import (
    DeploymentIntraday,
)
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.intraday import intraday_saver as _intraday_saver

DEPLOYMENT_INTRADAY = DeploymentIntraday()


@flow(**DEPLOYMENT_INTRADAY.saver_flow_decorator_args)
@enable_loguru_support
def intraday_saver(bus_date: datetime.date, tickers: list[str]) -> None:
    """Saver flow for intraday data.

    Args:
        bus_date (datetime.date): The business date.
        tickers (list[str]): List of stock tickers.
    """
    logger.info(
        f"Running Intraday saver for bus_date={bus_date}, tickers count={len(tickers)}"
    )
    _intraday_saver(bus_date=bus_date, tickers=tickers)


@flow(**DEPLOYMENT_INTRADAY.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def intraday_saver_dispatcher(
    bus_date: datetime.date, tickers: list[str] | None = None
) -> None:
    """Dispatcher flow for intraday data.

    Args:
        bus_date (datetime.date): The business date.
        tickers (list[str] | None): Optional list of tickers.
    """
    logger.info(f"Starting intraday_dispatcher_saver for {bus_date=}")

    if not tickers:
        raise ValueError("Tickers must be supplied for intraday_saver_dispatcher.")

    # Dispatch one saver per ticker for intraday (heavy data)

    params_list = [{"bus_date": bus_date, "tickers": [ticker]} for ticker in tickers]

    await DEPLOYMENT_INTRADAY.dispatch_sub_flows(params=params_list)
