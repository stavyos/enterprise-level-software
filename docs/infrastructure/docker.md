# Docker Overview

## What is Docker?
**Docker** is used in this project to provide isolated, reproducible environments for our databases and ETL workers.

## How we use it here

### 1. Database Isolation
We use **Docker Compose** to run two independent **TimescaleDB** instances on different ports. This ensures that development data never bleeds into production.

| Environment | Port | Container Name | Persistent Volume |
| :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `timescaledb_data_dev` |
| **Production** | `5435` | `timescaledb-prod` | `timescaledb_data_prod` |

**Startup Command**:
```bash
docker-compose up -d
```

### Windows Volume Mapping Fix

On Windows machines, absolute paths like `C:\path` trigger validation errors in Pydantic when used in Docker volumes because the colon is misinterpreted as a volume option separator.

We resolve this by automatically translating Windows paths in our `JobVariables` logic:
- **Input**: `C:\data`
- **Output**: `//c/data` (Docker Desktop compatible format)

This ensures that our Prefect worker can reliably bind host directories to the `/data` mount inside our ETL containers.

## CI/CD Orchestration & Networking

### Shared Network
A dedicated Docker network, `enterprise-network`, facilitates secure communication between services:
- **Jenkins**: Performs builds and triggers deployments on this network.
- **Prefect Server**: Accessible at `http://prefect-server:4200/api` within the network.
- **Agent Containers**: Dynamic build agents (custom Node/Python images) join this network to register flows.

### Advanced: Docker-in-Docker
The Jenkins container has access to the host's Docker engine via a socket mount (`/var/run/docker.sock`). This allows it to build, tag, and run the ETL images as part of the automated pipeline.
