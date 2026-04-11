"""Date range ETL flow module."""

import datetime

from loguru import logger
from prefect import flow

from etl_service.etl.deployments_settings.deployments.stocks.date_range import (
    DeploymentDateRange,
)
from etl_service.etl.flows.utils import enable_loguru_support

DEPLOYMENT_DATE_RANGE = DeploymentDateRange()


@flow(**DEPLOYMENT_DATE_RANGE.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def main_date_range_saver_dispatcher(bus_date: datetime.date) -> None:
    """Dispatcher flow for the date range saver.

    Args:
        bus_date (datetime.date): The business date.
    """
    logger.info(f"Starting main_date_range_saver_dispatcher for {bus_date=}")
    # TODO (syosef): Add any specific logic for date range saver dispatching here.
    pass
