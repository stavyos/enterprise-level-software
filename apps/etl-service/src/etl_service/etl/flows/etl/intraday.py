"""Intraday ETL flow module."""

import datetime

from etl_service.etl.deployments_settings.deployments.stocks.intraday import DeploymentIntraday
from etl_service.etl.flows.utils import enable_loguru_support
from loguru import logger
from prefect import flow

DEPLOYMENT_INTRADAY = DeploymentIntraday()


@flow(**DEPLOYMENT_INTRADAY.saver_flow_decorator_args)
@enable_loguru_support
def intraday_saver(bus_date: datetime.date) -> None:
    """Saver flow for intraday data.

    Args:
        bus_date (datetime.date): The business date.
    """
    logger.info(f"Running Intraday saver for bus_date={bus_date}")
    pass


@flow(**DEPLOYMENT_INTRADAY.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def intraday_saver_dispatcher(bus_date: datetime.date) -> None:
    """Dispatcher flow for intraday data.

    Args:
        bus_date (datetime.date): The business date.
    """
    logger.info(f"Starting intraday_dispatcher_saver for {bus_date=}")
    pass
