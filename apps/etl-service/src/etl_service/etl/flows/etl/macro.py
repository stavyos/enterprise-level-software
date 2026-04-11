"""Macro indicators flow module."""

import uuid
from etl_service.etl.deployments_settings.deployments.stocks.macro import DeploymentMacro
from etl_service.etl.flows.models.macro import EconomicIndicator, MacroSaveRequest
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.macro import macro_indicators_saver as _macro_indicators_saver
from loguru import logger
from prefect import flow

DEPLOYMENT_MACRO = DeploymentMacro()


@flow(**DEPLOYMENT_MACRO.saver_flow_decorator_args)
@enable_loguru_support
def macro_indicators_saver(save_request: MacroSaveRequest) -> None:
    """Flow task to save macro indicators."""
    logger.info(f"Running macro indicators saver for {save_request.country}")
    _macro_indicators_saver(
        country=save_request.country,
        indicator_codes=[i.indicator_code for i in save_request.indicators],
        run_id=save_request.run_id
    )


@flow(**DEPLOYMENT_MACRO.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def macro_indicators_saver_dispatcher(countries: list[str], indicators: list[str]) -> None:
    """Orchestrates macro indicators saving."""
    run_id = str(uuid.uuid4())
    
    params_list = [
        {
            "save_request": MacroSaveRequest(
                country=country,
                indicators=[EconomicIndicator(indicator_code=i) for i in indicators],
                run_id=run_id
            )
        }
        for country in countries
    ]

    await DEPLOYMENT_MACRO.dispatch_sub_flows(params=params_list)
