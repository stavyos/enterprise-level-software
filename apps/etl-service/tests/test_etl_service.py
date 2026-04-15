from etl_service.etl.deployments_settings.deps_utils import (
    get_deployment_flow_name,
    get_deployment_name,
)
from etl_service.etl.deployments_settings.enums import (
    PrefectDeployment,
    PrefectDeploymentType,
)
from etl_service.etl.deployments_settings.settings import settings


def test_deployment_naming_with_prefix():
    """Test that deployment and flow names correctly include the ENV_PREFIX."""
    original_prefix = settings.env_prefix
    try:
        # Test with prefix
        settings.env_prefix = "test-env"

        flow_name = get_deployment_flow_name(
            PrefectDeployment.STOCKS_EOD, PrefectDeploymentType.SAVER
        )
        assert flow_name == "test-env-STOCKS-EOD-SAVER"

        dep_name = get_deployment_name(
            PrefectDeployment.STOCKS_EOD, PrefectDeploymentType.SAVER
        )
        assert dep_name == "test-env-stocks_eod-saver-deployment"

        # Test without prefix
        settings.env_prefix = ""
        flow_name_no_prefix = get_deployment_flow_name(
            PrefectDeployment.STOCKS_EOD, PrefectDeploymentType.SAVER
        )
        assert flow_name_no_prefix == "STOCKS-EOD-SAVER"

        dep_name_no_prefix = get_deployment_name(
            PrefectDeployment.STOCKS_EOD, PrefectDeploymentType.SAVER
        )
        assert dep_name_no_prefix == "stocks_eod-saver-deployment"

    finally:
        # Restore original prefix
        settings.env_prefix = original_prefix
