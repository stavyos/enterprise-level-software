from __future__ import annotations

from etl_service.etl.deployments_settings.enums import (
    PrefectDeployment,
    PrefectDeploymentType,
)


def get_deployment_flow_name(
    deployment: PrefectDeployment, deployment_type: PrefectDeploymentType
) -> str:
    """Get deployment flow name."""
    from etl_service.etl.deployments_settings.settings import settings

    prefix = f"{settings.env_prefix}-" if settings.env_prefix else ""
    return f"{prefix}{deployment.value}-{deployment_type.value}"


def get_deployment_name(
    deployment: PrefectDeployment, deployment_type: PrefectDeploymentType
) -> str:
    """Get deployment name."""
    from etl_service.etl.deployments_settings.settings import settings

    dep = deployment.value.lower().replace("-", "_")
    type_ = deployment_type.value.lower()
    type_ = type_.replace(f"{dep}_", "")

    prefix = f"{settings.env_prefix}-" if settings.env_prefix else ""
    return f"{prefix}{dep}-{type_}-deployment"
