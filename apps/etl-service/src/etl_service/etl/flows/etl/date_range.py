"""Date range ETL flow module."""

import datetime

from loguru import logger
from prefect import flow

from etl_service.etl.deployments_settings.deployments.stocks.date_range import (
    DeploymentDateRange,
)
from etl_service.etl.deployments_settings.deployments.stocks.main import DeploymentMain
from etl_service.etl.flows.utils import enable_loguru_support, track_resources

DEPLOYMENT_DATE_RANGE = DeploymentDateRange()
DEPLOYMENT_MAIN = DeploymentMain()


@flow(**DEPLOYMENT_DATE_RANGE.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
@track_resources
async def main_date_range_saver_dispatcher(
    bus_date: datetime.date | None = None,
) -> None:
    """Dispatcher flow for the date range saver.

    Args:
        bus_date (datetime.date | None, optional): The business date. Defaults to None.
    """
    if not bus_date:
        bus_date = datetime.date.today()

    logger.info(f"Starting main_date_range_saver_dispatcher for {bus_date=}")

    # For now, it just triggers the main saver for the given bus_date
    await DEPLOYMENT_MAIN.dispatch_deployment_saver_dispatcher(
        parameters={"bus_date": bus_date}
    )
