# Jenkins CI/CD

## Overview
This project uses Jenkins for continuous integration and deployment. The pipeline is defined in a scripted `Jenkinsfile` at the root of the repository.

## Jenkins UI
Jenkins provides a web-based interface for managing builds and visualizing pipelines.
*   **Standard View**: Accessible via the main Jenkins URL (e.g., `http://localhost:8080`).
*   **Blue Ocean**: A modern, interactive visualization of the pipeline stages and logs.

## Pipeline Structure
The pipeline uses **Dockerized Stages** to ensure a consistent environment:

1.  **Set Environment**: Runs on the host; determines `dev` or `prod` based on the branch.
2.  **Setup & Tests (Dockerized)**: These stages run inside a `node:20-slim` container.
    *   Ensures that Node.js, npm, and Nx commands run in a Linux environment regardless of the host OS.
    *   `npm install` and `npm run test:all` are executed using `sh`.
3.  **Build**: Runs on the host to access the Docker daemon.
    *   Builds and tags the environment-specific image.
4.  **Deploy**: Runs on the host to register deployments with the Prefect server.

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
