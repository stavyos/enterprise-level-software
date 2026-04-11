"""Module for deploying Prefect flows for the ETL service."""

from etl_service.etl.deployments_settings.deployments.base import AbstractDeploymentSettings
from etl_service.etl.deployments_settings.enums import PrefectDeployment, PrefectDeploymentType
from etl_service.etl.deployments_settings.mapper import map_deployment_to_settings
from prefect.deployments.runner import RunnerDeployment
from prefect.deployments.runner import deploy as prefect_deploy


def deploy_flow(
    deployment_settings: AbstractDeploymentSettings,
    image: str | None,
    version_tag: str | None = None,
) -> list:
    """Creates RunnerDeployment objects for a specific Prefect flow.

    Args:
        deployment_settings (AbstractDeploymentSettings): The settings for the deployment.
        image (str | None): The Docker image to use for the deployment.
        version_tag (str | None, optional): A tag for the deployment version. Defaults to None.

    Returns:
        list: A list of RunnerDeployment objects.
    """
    deployments = []

    for dep_type in [PrefectDeploymentType.SAVER, PrefectDeploymentType.DISPATCHER]:
        is_available = deployment_settings.get_is_available(deployment_type=dep_type)
        if not is_available:
            continue

        dep_name = deployment_settings.get_deployment_name(deployment_type=dep_type)
        dep_run_name = deployment_settings.get_deployment_run_name(deployment_type=dep_type)

        job_variables = deployment_settings.get_job_variables(deployment_type=dep_type)

        if not job_variables:
            msg = f"No job variables for {dep_run_name}, using default values"
            raise ValueError(msg)

        tags = [version_tag] if version_tag else []
        tags += ["etl", deployment_settings.deployment.value]

        concurrency_limit = deployment_settings.get_concurrency_limit(deployment_type=dep_type)

        # Entrypoint relative to the container's PYTHONPATH (/app/apps/etl-service/src)
        module_path = deployment_settings.flows_module.replace(".py", "")
        flow_function_name = deployment_settings.get_entry_point(deployment_type=dep_type).split(
            ":"
        )[-1]
        entrypoint = f"etl_service.etl.flows.etl.{module_path}:{flow_function_name}"

        # Use RunnerDeployment constructor directly to avoid auto-detecting absolute host paths.
        d = RunnerDeployment(
            entrypoint=entrypoint,
            name=dep_name,
            flow_name=deployment_settings.get_flow_name(deployment_type=dep_type),
            tags=tags,
            concurrency_limit=concurrency_limit,
            job_variables=job_variables.to_dict(),
            schedules=deployment_settings.get_schedules(deployment_type=dep_type),
        )
        deployments.append(d)

    return deployments


def deploy(image: str | None = None, version_tag: str | None = None) -> None:
    """Iterates through all defined Prefect deployments and registers them.

    Args:
        image (str | None, optional): The Docker image to use for all deployments. Defaults to None.
        version_tag (str | None, optional): A version tag for all deployments. Defaults to None.
    """
    all_deployments = []
    for prefect_dep in PrefectDeployment:
        dep_settings = map_deployment_to_settings(deployment=prefect_dep)
        all_deployments.extend(
            deploy_flow(deployment_settings=dep_settings, image=image, version_tag=version_tag)
        )

    # build=False tells Prefect the code is already in the image.
    prefect_deploy(
        *all_deployments,
        work_pool_name=AbstractDeploymentSettings.WORK_POOL,
        image=image,
        build=False,
    )


if __name__ == "__main__":
    deploy(image="etl-service:local")
