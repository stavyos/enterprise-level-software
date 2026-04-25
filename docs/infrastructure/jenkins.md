# Jenkins CI/CD

## Overview
This project uses Jenkins for continuous integration and deployment. The pipeline is defined in a scripted `Jenkinsfile` at the root of the repository.

## Jenkins UI
Jenkins provides a web-based interface for managing builds and visualizing pipelines.
*   **Standard View**: Accessible via the main Jenkins URL (default: `http://localhost:8080`).
*   **Blue Ocean**: A modern, interactive visualization of the pipeline stages and logs.

## How to Start Jenkins (Docker)
To run Jenkins locally using Docker, use the following command. This version includes the Docker CLI inside Jenkins so it can build your project images:

```bash
docker run -d `
  --name jenkins `
  -p 8080:8080 -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v /var/run/docker.sock:/var/run/docker.sock `
  jenkins/jenkins:lts
```

**Note for Windows users**: Ensure Docker Desktop is running and "Expose daemon on tcp://localhost:2375 without TLS" is enabled, or use the WSL2 backend.

Once started:
1.  Navigate to `http://localhost:8080`.
2.  Retrieve the initial admin password: `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword`.
3.  Install suggested plugins and create your first admin user.

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
