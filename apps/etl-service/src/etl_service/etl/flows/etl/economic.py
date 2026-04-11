"""Economic events flow module."""

import datetime
import uuid
from etl_service.etl.deployments_settings.deployments.stocks.economic import DeploymentEconomic
from etl_service.etl.flows.models.economic import EconomicSaveRequest
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.economic import economic_events_saver as _economic_events_saver
from loguru import logger
from prefect import flow

DEPLOYMENT_ECONOMIC = DeploymentEconomic()


@flow(**DEPLOYMENT_ECONOMIC.saver_flow_decorator_args)
@enable_loguru_support
def economic_events_saver(save_request: EconomicSaveRequest) -> None:
    """Flow task to save economic events."""
    logger.info(f"Running economic events saver for {save_request.from_date} to {save_request.to_date}")
    _economic_events_saver(
        from_date=save_request.from_date,
        to_date=save_request.to_date,
        country=save_request.country,
        run_id=save_request.run_id
    )


@flow(**DEPLOYMENT_ECONOMIC.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def economic_events_saver_dispatcher(from_date: datetime.date, to_date: datetime.date, countries: list[str] | None = None) -> None:
    """Orchestrates economic events saving."""
    run_id = str(uuid.uuid4())
    
    if not countries:
        countries = [None] # Fetch global if no country specified

    params_list = [
        {
            "save_request": EconomicSaveRequest(
                from_date=from_date,
                to_date=to_date,
                country=country,
                run_id=run_id
            )
        }
        for country in countries
    ]

    await DEPLOYMENT_ECONOMIC.dispatch_sub_flows(params=params_list)
