# Environment Parity (Twelve-Factor App)

## Overview
This project strictly follows the **Twelve-Factor App** principles for building modern, cloud-native software. We aim to keep our development and production environments as identical as possible to eliminate "it works on my machine" issues.

## 1. Codebase (One Codebase, Many Deploys)
We maintain a single repository for each microservice. The same code runs in both development and production, with only configuration changes distinguishing the two.

## 2. Config (Store Config in the Environment)
We strictly separate configuration from code.
- **Sensitive Data**: We use `.env` files (e.g., `dev.env`, `prod.env`) for local development, ensuring these are **never committed** to Git.
- **Templates**: We provide `template.dev.env` and `template.prd.env` to document required variables and offer helpful defaults like `ENV_PREFIX=dev`.
- **Environment Variables**: At runtime, config is loaded from the environment, making the application portable and secure.

## 3. Dev/Prod Parity
We minimize gaps between development and production across three dimensions:

| Gap | Traditional Approach | Our Twelve-Factor Approach |
| :--- | :--- | :--- |
| **Time Gap** | Developer works on code for weeks/months. | Developers use isolated worktrees and PRs for frequent, small updates. |
| **Personnel Gap** | Developers write code; Ops engineers deploy it. | Developers manage the end-to-end lifecycle (implementation, testing, deployment). |
| **Tools Gap** | Dev uses local SQLite; Prod uses PostgreSQL. | Both environments use **TimescaleDB** (PostgreSQL) via Docker, ensuring identical database behavior. |

## 4. Backing Services
We treat backing services (databases, message queues, caches) as "attached resources."
- Our ETL service connects to TimescaleDB via a standard URI, which can easily be swapped between local Docker and managed cloud services without code changes.

## 5. Build, Release, Run
We strictly separate the deployment process into three distinct stages:
1.  **Build**: Compiling code and building a Docker image (`etl-service:dev`).
2.  **Release**: Combining the build with environment-specific config (`ENV_PREFIX=dev`).
3.  **Run**: Executing the application in its specific execution environment (Kubernetes).

## 6. Port Binding
Our services are self-contained and export themselves via port binding.
- **Prefect**: Runs on port 4200.
- **TimescaleDB (Dev)**: Runs on port 5434.
- **TimescaleDB (Prod)**: Runs on port 5435.
