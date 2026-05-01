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
    bus_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    tickers: list[str] = None,
) -> None:
    """Dispatcher flow for intraday data.

    Args:
        bus_date (datetime.date | None, optional): Start business date. Defaults to today.
        end_date (datetime.date | None, optional): End business date for range fetch.
        tickers (list[str]): List of stock tickers.
    """
    if not bus_date:
        bus_date = datetime.date.today()

    if not tickers:
        raise ValueError("Tickers must be supplied for intraday_saver_dispatcher.")

    # Determine dates to process
    if end_date:
        if end_date < bus_date:
            raise ValueError(f"end_date ({end_date}) must be >= bus_date ({bus_date})")

        logger.info(f"Starting intraday backfill from {bus_date} to {end_date}")

        # Calculate all days in range
        delta = end_date - bus_date
        dates = [bus_date + datetime.timedelta(days=i) for i in range(delta.days + 1)]
    else:
        logger.info(f"Starting single-day intraday fetch for {bus_date}")
        dates = [bus_date]

    # Dispatch one saver per ticker per day
    # NOTE: Even for long ranges, we dispatch daily savers to stay within
    # 90-day API limits for 1-minute data and ensure failure isolation.
    params_list = []
    for d in dates:
        # Skip weekends for stock data
        if d.weekday() >= 5:  # 5=Saturday, 6=Sunday
            continue

        for ticker in tickers:
            params_list.append({"bus_date": d, "tickers": [ticker]})

    if not params_list:
        logger.warning("No valid business days found in the requested range.")
        return

    logger.info(f"Dispatching {len(params_list)} total sub-flows.")
    await DEPLOYMENT_INTRADAY.dispatch_sub_flows(params=params_list)
