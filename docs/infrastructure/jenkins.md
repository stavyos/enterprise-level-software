# Jenkins CI/CD

## Overview
This project uses Jenkins for continuous integration and deployment. The pipeline is defined in a scripted `Jenkinsfile` at the root of the repository.

## Pipeline Structure
The pipeline consists of the following stages:

1.  **Set Environment**: Determines the target environment (`dev` or `prod`) based on the branch name.
    *   `master` or `main` branches deploy to `prod`.
    *   All other branches (including Pull Requests) deploy to `dev`.
2.  **Setup**: Installs project dependencies.
    *   `npm install`: Installs Node.js dependencies and Nx.
    *   `npm run install:all`: Uses Nx to install Python dependencies via `uv` for all applications and libraries.
3.  **Tests**: Executes all tests across the monorepo using `npm run test:all`.
4.  **Build**: Builds a Docker image for the ETL service.
    *   Uses `Dockerfile.etl`.
    *   Tags the image with the environment name (e.g., `etl-service:dev`).
    *   Passes `ENV_PREFIX` as a build argument.
5.  **Deploy**: Registers flows with the Prefect server.
    *   Uses the environment-specific Docker image.
    *   Sets `ENV_PREFIX` environment variable during registration.

## Environment Isolation
Isolation between `dev` and `prod` is maintained through:
*   **Docker Tags**: Environment-specific images (`etl-service:dev`, `etl-service:prod`).
*   **Env Prefix**: Used to distinguish deployments and flows in the Prefect UI.
*   **Configuration**: Environment-specific `.env` files (loaded during runtime in the container or via `ENV_PREFIX` during deployment).
*   **Templates**: `template.dev.env` and `template.prod.env` provide the structure for environment-specific configuration.

## Requirements
*   Jenkins with `Pipeline` plugin.
*   Node.js and npm installed on the Jenkins runner.
*   `uv` installed and available in the PATH.
*   Docker installed and accessible by the Jenkins user.
*   Prefect server accessible from the Jenkins runner.
