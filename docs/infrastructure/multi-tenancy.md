# Multi-Tenancy Strategy (Environment Isolation)

## Overview
This project employs a **Single-Cluster Multi-Tenancy** strategy for its orchestration layer. We use a single Prefect server to manage multiple environments (Development and Production), ensuring resource efficiency while maintaining strict isolation between different deployment stages.

## Why We Use a Single Cluster
1.  **Reduced Overhead**: Running separate Prefect servers for each environment increases complexity, resource consumption (CPU/Memory), and management effort.
2.  **Simplified Monitoring**: A central dashboard provides a single source of truth for all data pipelines across the organization.
3.  **Local Development Parity**: Developers interact with the same infrastructure patterns they use in production.

## Isolation Mechanisms

### 1. Prefect Naming Conventions (Prefixed Flows)
Isolation is enforced through the `ENV_PREFIX` environment variable. The `deployments_settings` utility dynamically generates names:
- **Flow Name**: `{prefix}/FLOW-NAME` (e.g., `dev/STOCKS-EOD-SAVER`)
- **Deployment Name**: `{prefix}-FLOW-NAME-deployment` (e.g., `prd-stocks_eod-saver-deployment`)

This grouping allows for easy filtering in the Prefect UI and prevents accidental overwrites when deploying to a shared cluster.

### 2. Docker Image Baking
Instead of mounting volumes or using shared filesystems, we "bake" environment-specific configurations into Docker images during the build process:
- **Image Tags**: `etl-service:dev` vs `etl-service:prd`
- **Configuration**: Environment variables like `DB_PORT`, `ENV_PREFIX`, and `DB_NAME` are set as `ENV` within the image.

### 3. Database Isolation (TimescaleDB)
Each environment targets a dedicated database instance:
- **Dev**: `timescaledb-dev` on port 5434
- **Prod**: `timescaledb-prod` on port 5435

### 4. Kubernetes Resources
By leveraging Prefect's `job_variables`, we can define different resource limits per environment (e.g., production savers get more CPU/Memory than development ones).

### 5. Physical Data Isolation (Parquet)
Intraday data stored on the host filesystem is strictly isolated by environment-specific root directories:
- **Development**: `C:/enterprise-level-software/data/dev/intraday`
- **Production**: `C:/enterprise-level-software/data/prd/intraday`

This ensures that development backfills or experimental runs never pollute production datasets. On Windows host machines, these paths are automatically translated to Docker-compatible formats (e.g., `//c/path`) within the `JobVariables` layer.

## The Work Pool Job Template Guard
A critical discovery during our implementation was that Prefect **Work Pools** (specifically Docker/K8s types) come with a "Base Job Template."

> **Important**: If the Work Pool template has hardcoded environment variables (e.g., `DB_PORT=5430`), these will override any variables provided in the deployment's `job_variables`. We ensure our work pools are created with clean templates to allow our dynamic, environment-aware settings to take precedence.

## Twelve-Factor App Principles
Our multi-tenancy strategy aligns with several "Twelve-Factor App" principles:
- **Config**: Strict separation of config from code (stored in environment variables).
- **Dev/Prod Parity**: Keeping development, staging, and production as similar as possible.
- **Processes**: Execute the app as one or more stateless processes.
