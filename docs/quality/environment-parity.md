# Environment Parity (Twelve-Factor App)

## Overview
This project strictly follows the **Twelve-Factor App** principles for building modern, cloud-native software. We aim to keep our development and production environments as identical as possible to eliminate "it works on my machine" issues.

## 1. Codebase (One Codebase, Many Deploys)
We maintain a single repository for each microservice. The same code runs in both development and production, with only configuration changes distinguishing the two.

## 2. Config (Store Config in the Environment)
We strictly separate configuration from code.
- **Sensitive Data**: We use `.env` files (e.g., `dev.env`, `prod.env`) for local development, ensuring these are **never committed** to Git.
- **Templates**: We provide `template.dev.env` and `template.prod.env` to document required variables and offer helpful defaults like `ENV_PREFIX=dev`.
- **Environment Variables**: At runtime, config is loaded from the environment, making the application portable and secure.

## 3. Dynamic Host Resolution (The Parity Bridge)
One of the hardest gaps to bridge is how services talk to each other when one is on the host and another is in a container.

We implemented **Dynamic Host Resolution** in our `Settings` class:
- **Database**: If `DB_HOST` is set to `localhost` but the code is running inside a container, it dynamically resolves to `host.docker.internal`.
- **Orchestration**: The `PREFECT_API_URL` also dynamically switches from `localhost` to `host.docker.internal` when executing within a Docker worker.

This allows the exact same configuration files (`dev.env`) to work seamlessly whether you are running a script locally or triggering a flow inside a container.

## 4. Dev/Prod Parity
We minimize gaps between development and production across three dimensions:

| Gap | Traditional Approach | Our Twelve-Factor Approach |
| :--- | :--- | :--- |
| **Time Gap** | Developer works on code for weeks/months. | Developers use isolated worktrees and PRs for frequent, small updates. |
| **Personnel Gap** | Developers write code; Ops engineers deploy it. | Developers manage the end-to-end lifecycle (implementation, testing, deployment). |
| **Tools Gap** | Dev uses local SQLite; Prod uses PostgreSQL. | Both environments use **TimescaleDB** (PostgreSQL) via Docker, ensuring identical database behavior. |

## 5. Backing Services
We treat backing services (databases, message queues, caches) as "attached resources."
- Our ETL service connects to TimescaleDB via a standard URI, which can easily be swapped between local Docker and managed cloud services without code changes.

## 6. Build, Release, Run
We strictly separate the deployment process into three distinct stages:
1.  **Build**: Compiling code and building a Docker image (`etl-service:dev`).
2.  **Release**: Combining the build with environment-specific config (`ENV_PREFIX=dev`).
3.  **Run**: Executing the application in its specific execution environment (Kubernetes).

## 7. Port Binding
Our services are self-contained and export themselves via port binding.
- **Prefect**: Runs on port 4200.
- **TimescaleDB (Dev)**: Runs on port 5434.
- **TimescaleDB (Prod)**: Runs on port 5435.
- **Parquet Storage**: Dev data is mapped to `/data/dev` while Prod uses `/data/prd`.
