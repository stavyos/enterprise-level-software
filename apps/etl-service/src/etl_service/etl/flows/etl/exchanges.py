"""Exchanges ETL flow module."""

import datetime

from etl_service.etl.deployments_settings.deployments.stocks.exchanges import DeploymentExchanges
from etl_service.etl.flows.utils import enable_loguru_support
from loguru import logger
from prefect import flow

DEPLOYMENT_EXCHANGES = DeploymentExchanges()


@flow(**DEPLOYMENT_EXCHANGES.saver_flow_decorator_args)
@enable_loguru_support
def exchanges_saver(bus_date: datetime.date) -> None:
    """Saver flow for exchanges data.

    Args:
        bus_date (datetime.date): The business date.
    """
    logger.info(f"Running Exchanges saver for bus_date={bus_date}")
    pass


@flow(**DEPLOYMENT_EXCHANGES.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def exchanges_saver_dispatcher(bus_date: datetime.date) -> None:
    """Dispatcher flow for exchanges data.

    Args:
        bus_date (datetime.date): The business date.
    """
    logger.info(f"Starting exchanges_dispatcher_saver for {bus_date=}")
    pass
