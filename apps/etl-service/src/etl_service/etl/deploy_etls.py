"""Module for deploying Prefect flows for the ETL service."""

import asyncio

from prefect.deployments.runner import RunnerDeployment
from prefect.deployments.runner import deploy as prefect_deploy

from etl_service.etl.deployments_settings.enums import (
    PrefectDeployment,
    PrefectDeploymentType,
)
from etl_service.etl.deployments_settings.mapper import map_deployment_to_settings


async def deploy(image: str | None = None, version_tag: str | None = None) -> None:
    """Iterates through all defined Prefect deployments and registers them.

    Args:
        image (str | None, optional): The Docker image to use for all deployments. Defaults to None.
        version_tag (str | None, optional): A version tag for all deployments. Defaults to None.
    """
    # Group deployments by work pool
    pool_deployments = {}

    from etl_service.etl.deployments_settings.settings import settings

    for prefect_dep in PrefectDeployment:
        dep_settings = map_deployment_to_settings(deployment=prefect_dep)

        for dep_type in [PrefectDeploymentType.SAVER, PrefectDeploymentType.DISPATCHER]:
            is_available = dep_settings.get_is_available(deployment_type=dep_type)
            if not is_available:
                continue

            flow_name = dep_settings.get_flow_name(deployment_type=dep_type)
            dep_name = dep_settings.get_deployment_name(deployment_type=dep_type)
            job_variables = dep_settings.get_job_variables(
                deployment_type=dep_type
            ).to_dict()

            if image:
                job_variables["image"] = image

            # Ensure PYTHONPATH is set in job variables for Docker
            if "env" not in job_variables:
                job_variables["env"] = {}
            job_variables["env"]["PYTHONPATH"] = settings.job_pythonpath

            tags = [version_tag] if version_tag else []
            tags += ["etl", dep_settings.deployment.value]
            if settings.env_prefix:
                tags.append(settings.env_prefix)

            # Get entrypoint
            module_path = dep_settings.flows_module.replace(".py", "")
            ep = dep_settings.get_entry_point(deployment_type=dep_type)
            flow_function_name = ep.split(":")[-1]
            entrypoint = f"etl_service.etl.flows.etl.{module_path}:{flow_function_name}"

            # Create deployment specification
            d = RunnerDeployment(
                name=dep_name,
                flow_name=flow_name,
                entrypoint=entrypoint,
                tags=tags,
                job_variables=job_variables,
            )

            work_pool = dep_settings.work_pool
            if work_pool not in pool_deployments:
                pool_deployments[work_pool] = []
            pool_deployments[work_pool].append(d)

    # Register each pool's deployments
    for pool_name, deployments in pool_deployments.items():
        print(f"Deploying {len(deployments)} flows to pool: {pool_name}")
        await prefect_deploy(
            *deployments, work_pool_name=pool_name, image=image, build=False, push=False
        )


if __name__ == "__main__":
    import sys

    from etl_service.etl.deployments_settings.settings import settings

    default_img = (
        f"etl-service:{settings.env_prefix}"
        if settings.env_prefix
        else "etl-service:dev"
    )
    img = sys.argv[1] if len(sys.argv) > 1 else default_img

    print(f"Deploying using image: {img}")
    asyncio.run(deploy(image=img))
