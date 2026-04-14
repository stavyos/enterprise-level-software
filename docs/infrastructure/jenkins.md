# Multi-Environment Jenkins CI/CD Documentation

This document describes the automated multi-environment CI/CD pipeline for the enterprise-level software project.

## CI/CD Workflow

The Jenkins pipeline is defined in the root `Jenkinsfile` and uses a parameterized approach to support both `DEV` and `PROD` environments.

### Environment Selection

When triggering a build from the Jenkins UI, users can select the `ENVIRONMENT` parameter:
-   **DEV**: Targets the development Prefect cluster (port 4200) and uses `.env.dev`. Tags Docker images with `dev`.
-   **PROD**: Targets the production Prefect cluster (port 4201) and uses `.env.prod`. Tags Docker images with `prod`.

### Pipeline Stages

1.  **Set Environment**: Configures environment variables based on the selected `ENVIRONMENT` parameter.
2.  **Setup**:
    -   Installs Node.js dependencies (`npm install`).
    -   Installs project dependencies (`npx nx run-many -t install`).
    -   Runs code quality checks using `ruff` (`uv run ruff check .`).
3.  **Tests**: Executes automated tests for all apps and libs in the monorepo (`npx nx run-many -t test`).
4.  **Build**:
    -   Builds the Docker image for the `etl-service`.
    -   Tags the image based on the environment (`etl-service:dev` or `etl-service:prod`).
5.  **Publish**:
    -   **Placeholder Stage**: Intended for pushing the built Docker image to a remote repository such as AWS ECR.
6.  **Deploy**:
    -   Uses `python-dotenv` to load the correct environment file (`.env.dev` or `.env.prod`).
    -   Registers the Prefect flows as deployments using `npx nx run etl-service:deploy`.

### Prerequisites for Jenkins Nodes

To run this pipeline, the Jenkins build node must have:
-   **Node.js & npm**: For Nx and dependency management.
-   **Python & uv**: For managing Python virtual environments.
-   **Docker**: For building and tagging container images.
-   **Git**: For code checkout.
-   **python-dotenv CLI**: For loading environment variables from `.env` files.

## Environment Variables

-   `PREFECT_API_URL`: Dynamically set based on the environment.
-   `DOCKER_TAG`: Dynamically set to `dev` or `prod`.
-   `ENV_FILE`: Path to the environment configuration file.

## Usage
1.  Open the Jenkins job.
2.  Click **Build with Parameters**.
3.  Select `DEV` or `PROD` from the `ENVIRONMENT` dropdown.
4.  Click **Build**.
