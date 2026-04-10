# Kubernetes and Prefect Setup Guide

This guide outlines the steps to set up a local development environment using Docker Desktop's Kubernetes, Prefect for workflow orchestration, and the connection between the two.

## 1. Set Up Kubernetes (K8s)
**Action**: Install Docker Desktop and enable its built-in Kubernetes cluster in the settings.

- **What it is**: Kubernetes is an open-source system for automating deployment and management of containerized applications.
- **Why we do this**: It provides a local, isolated environment to simulate production-like container orchestration. This allows us to test our Prefect flows in an environment that mirrors production (K8s Jobs).

### Verify Your Cluster
```powershell
# Check that your context is set to docker-desktop
kubectl config current-context

# Check the nodes of your cluster
kubectl get nodes
```

## 2. Set Up Prefect Orchestrator
**Action**: Synchronize dependencies and start the local Prefect server.

- **What it is**: Prefect is our orchestration tool. The local server provides a web interface (UI) to manage flows and monitor runs.
- **Why we do this**: The local server is essential for observing flow execution and debugging logic before deploying to higher environments.

### Project Configuration
Our `apps/prefect-orchestrator` is configured with specific Nx targets for ease of use:

**`project.json` excerpt:**
```json
"targets": {
  "run": {
    "executor": "nx:run-commands",
    "options": {
      "command": "uv run prefect server start",
      "cwd": "{projectRoot}"
    }
  },
  "worker": {
    "executor": "nx:run-commands",
    "options": {
      "command": "uv run prefect worker start --pool my-k8s-pool",
      "cwd": "{projectRoot}"
    }
  }
}
```

### Execution
```bash
# Install dependencies
npx nx run prefect-orchestrator:install

# Start the server
npx nx run prefect-orchestrator:run
```

## 3. Configure the Prefect API
**Action**: Point your Prefect client to the local server.

```bash
uv run prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
```

> [!TIP]
> **Persistence**: To avoid running this command in every new terminal, add `PREFECT_API_URL=http://127.0.0.1:4200/api` to your `.env` file at the root of the project.

## 4. Connect Prefect & K8s (Work Pool)
**Action**: Create a "Kubernetes Work Pool" in the Prefect UI.

1. Go to [http://127.0.0.1:4200](http://127.0.0.1:4200).
2. Click **Work Pools** -> **+** -> **Kubernetes**.
3. Name it: `my-k8s-pool`.
4. Save.

- **Why we do this**: This establishes the link between Prefect's orchestration and Kubernetes' execution. It tells Prefect that flows assigned to this pool should run as K8s Pods.

## 5. Start a Worker
**Action**: Run a worker to bridge the two systems.

- **What it is**: The worker polls the Prefect server and initiates the K8s Job execution.
- **Why we do this**: Without a worker, the Work Pool will remain "Inactive" and flows will stay in a "Pending" state.

```bash
# Using the pre-configured Nx target
npx nx run prefect-orchestrator:worker
```

## Troubleshooting & Tips
- **Image Pulls**: Since we are using a local cluster, ensure your Docker images are either built locally (and visible to the `docker-desktop` context) or hosted in an accessible registry.
- **Resources**: If a flow fails with `OOMKilled`, check the `JobVariables` in your deployment settings to increase Memory limits.


## 6. Register Deployments
**Action**: Run the deployment script to register all ETL flows with the Prefect server.

- **What it is**: This script iterates through all defined ETL settings and creates corresponding Deployments in Prefect.
- **Why we do this**: Without registration, the Prefect server won't know which flows are available to be scheduled or run.

``bash
npx nx run etl-service:deploy
``


## 6. Docker Build
**Action**: Build the local Docker image before registering deployments.

``bash
npx nx run etl-service:docker-build
``
