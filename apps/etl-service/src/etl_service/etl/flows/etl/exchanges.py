"""Exchanges ETL flow module."""

from loguru import logger
from prefect import flow

from etl_service.etl.deployments_settings.deployments.stocks.exchanges import (
    DeploymentExchanges,
)
from etl_service.etl.flows.utils import enable_loguru_support, track_resources

DEPLOYMENT_EXCHANGES = DeploymentExchanges()


@flow(**DEPLOYMENT_EXCHANGES.saver_flow_decorator_args)
@enable_loguru_support
@track_resources
def exchanges_saver() -> None:
    """Saver flow for exchanges data."""
    from etl_service.etl.scripts.exchanges import exchanges_saver as run_exchanges_saver

    logger.info("Running Exchanges saver")
    run_exchanges_saver()


@flow(**DEPLOYMENT_EXCHANGES.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
@track_resources
async def exchanges_saver_dispatcher() -> None:
    """Dispatcher flow for exchanges data."""
    logger.info("Starting exchanges_dispatcher_saver")

    params_list = [{}]

    await DEPLOYMENT_EXCHANGES.dispatch_sub_flows(params=params_list)
