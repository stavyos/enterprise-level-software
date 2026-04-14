"""Exchanges ETL flow module."""

import datetime

from loguru import logger
from prefect import flow

from etl_service.etl.deployments_settings.deployments.stocks.exchanges import (
    DeploymentExchanges,
)
from etl_service.etl.flows.utils import enable_loguru_support

DEPLOYMENT_EXCHANGES = DeploymentExchanges()


@flow(**DEPLOYMENT_EXCHANGES.saver_flow_decorator_args)
@enable_loguru_support
def exchanges_saver(bus_date: datetime.date) -> None:
    """Saver flow for exchanges data.

    Args:
        bus_date (datetime.date): The business date.
    """
    from etl_service.etl.scripts.exchanges import exchanges_saver as run_exchanges_saver

    logger.info(f"Running Exchanges saver for bus_date={bus_date}")
    run_exchanges_saver(bus_date=bus_date)


@flow(**DEPLOYMENT_EXCHANGES.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def exchanges_saver_dispatcher(bus_date: datetime.date | None = None) -> None:
    """Dispatcher flow for exchanges data.

    Args:
        bus_date (datetime.date | None, optional): The business date. Defaults to None.
    """
    if not bus_date:
        bus_date = datetime.date.today()

    logger.info(f"Starting exchanges_dispatcher_saver for {bus_date=}")

    params_list = [{"bus_date": bus_date}]

    await DEPLOYMENT_EXCHANGES.dispatch_sub_flows(params=params_list)
