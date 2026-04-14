# Docker Overview

## What is Docker?
**Docker** is an open-source platform that automates the deployment, scaling, and management of applications by using **containers**.

## Popular Commands
| Command | Description |
| :--- | :--- |
| `docker-compose up -d` | Start all services defined in `docker-compose.yaml`. |
| `docker-compose down` | Stop and remove all containers. |
| `docker ps` | List all running containers. |
| `docker logs <name>` | See the output/logs of a container. |

## How we use it here
In this project, we use **Docker Compose** to manage separate **TimescaleDB** instances for data isolation between development and production.

### Service Mapping

| Environment | Port | Container Name | Persistent Volume |
| :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `timescaledb_data_dev` |
| **Production** | `5435` | `timescaledb-prod` | `timescaledb_data_prod` |

### Infrastructure Lifecycle
To start both database instances:
```bash
docker-compose up -d
```

To stop all instances:
```bash
docker-compose down
```
