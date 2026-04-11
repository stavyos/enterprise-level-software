from etl_service.etl.deployments_settings.deployments.base import AbstractDeploymentSettings
from etl_service.etl.deployments_settings.deployments.stocks.bulk import DeploymentBulk
from etl_service.etl.deployments_settings.deployments.stocks.date_range import DeploymentDateRange
from etl_service.etl.deployments_settings.deployments.stocks.economic import DeploymentEconomic
from etl_service.etl.deployments_settings.deployments.stocks.eod import DeploymentEOD
from etl_service.etl.deployments_settings.deployments.stocks.exchanges import DeploymentExchanges
from etl_service.etl.deployments_settings.deployments.stocks.fundamentals import DeploymentFundamentals
from etl_service.etl.deployments_settings.deployments.stocks.intraday import DeploymentIntraday
from etl_service.etl.deployments_settings.deployments.stocks.macro import DeploymentMacro
from etl_service.etl.deployments_settings.deployments.stocks.main import DeploymentMain
from etl_service.etl.deployments_settings.deployments.stocks.news import DeploymentNews
from etl_service.etl.deployments_settings.deployments.stocks.technical import DeploymentTechnical
from etl_service.etl.deployments_settings.enums import PrefectDeployment


def map_deployment_to_settings(deployment: PrefectDeployment) -> AbstractDeploymentSettings:
    match deployment:
        case PrefectDeployment.MAIN:
            return DeploymentMain()
        case PrefectDeployment.MAIN_DATE_RANGE:
            return DeploymentDateRange()
        case PrefectDeployment.EOD:
            return DeploymentEOD()
        case PrefectDeployment.INTRADAY:
            return DeploymentIntraday()
        case PrefectDeployment.EXCHANGES:
            return DeploymentExchanges()
        case PrefectDeployment.FUNDAMENTALS:
            return DeploymentFundamentals()
        case PrefectDeployment.ECONOMIC_EVENTS:
            return DeploymentEconomic()
        case PrefectDeployment.MACRO_INDICATORS:
            return DeploymentMacro()
        case PrefectDeployment.MARKET_NEWS:
            return DeploymentNews()
        case PrefectDeployment.TECHNICAL_INDICATORS:
            return DeploymentTechnical()
        case PrefectDeployment.BULK_DATA:
            return DeploymentBulk()
        case _:
            raise NotImplementedError(f"Mapping for deployment {deployment} is not implemented.")
