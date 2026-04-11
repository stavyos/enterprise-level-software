"""Bulk data flow module."""

import datetime
import uuid

from etl_service.etl.deployments_settings.deployments.stocks.bulk import DeploymentBulk
from etl_service.etl.flows.models.bulk import BulkDataSaveRequest
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.bulk import bulk_data_saver as _bulk_data_saver
from loguru import logger
from prefect import flow

DEPLOYMENT_BULK = DeploymentBulk()


@flow(**DEPLOYMENT_BULK.saver_flow_decorator_args)
@enable_loguru_support
def bulk_data_saver(save_request: BulkDataSaveRequest) -> None:
    """Flow task to save bulk data."""
    logger.info(f"Running bulk data saver for {save_request.country} type={save_request.type}")
    _bulk_data_saver(
        country=save_request.country,
        bus_date=save_request.bus_date,
        data_type=save_request.type,
        run_id=save_request.run_id,
    )


@flow(**DEPLOYMENT_BULK.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def bulk_data_saver_dispatcher(
    countries: list[str], bus_date: datetime.date, data_types: list[str] | None = None
) -> None:
    """Orchestrates bulk data saving."""
    run_id = str(uuid.uuid4())

    if not data_types:
        data_types = ["eod", "splits", "dividends"]

    params_list = []
    for country in countries:
        for dt in data_types:
            params_list.append(
                {
                    "save_request": BulkDataSaveRequest(
                        country=country, bus_date=bus_date, type=dt, run_id=run_id
                    )
                }
            )

    await DEPLOYMENT_BULK.dispatch_sub_flows(params=params_list)
