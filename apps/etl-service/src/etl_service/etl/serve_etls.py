"""Script for serving Prefect flows locally for development."""

import asyncio
import os

from etl_service.etl.deployments_settings.enums import (
    PrefectDeployment,
    PrefectDeploymentType,
)
from etl_service.etl.deployments_settings.mapper import map_deployment_to_settings
from etl_service.etl.deployments_settings.settings import settings


async def serve_all():
    deployments = []

    # Mark as local runner
    os.environ["PREFECT_RUNNER"] = "true"

    # Ensure settings are loaded from the environment this script is running in
    settings.reload()

    # Get all environment variables to propagate to the flows
    env_vars = {
        k: v
        for k, v in os.environ.items()
        if k in settings.model_fields or k.startswith("PREFECT_")
    }

    # Explicitly add the settings we want to override for local process workers
    env_vars["DB_PORT"] = str(settings.db_port)
    env_vars["DB_HOST"] = settings.db_host
    env_vars["IS_LOCAL"] = "true"

    for prefect_dep in PrefectDeployment:
        dep_settings = map_deployment_to_settings(deployment=prefect_dep)

        for dep_type in [PrefectDeploymentType.SAVER, PrefectDeploymentType.DISPATCHER]:
            if not dep_settings.get_is_available(dep_type):
                continue

            flow_function = dep_settings.get_flow_function(dep_type)
            if not flow_function:
                continue

            dep_name = dep_settings.get_deployment_name(dep_type)

            # Create job variables, merging existing with current env
            job_vars = dep_settings.get_job_variables(dep_type).to_dict()
            if "env" not in job_vars:
                job_vars["env"] = {}
            job_vars["env"].update(env_vars)

            # Create a deployment object for serving
            deployment = await flow_function.to_deployment(
                name=dep_name,
                work_pool_name=dep_settings.work_pool,
                job_variables=job_vars,
            )
            deployments.append(deployment)

    print(f"Serving {len(deployments)} deployments on pools...")
    from prefect import aserve

    await aserve(*deployments)


if __name__ == "__main__":
    asyncio.run(serve_all())
