# Docker Overview

## What is Docker?
**Docker** is an open-source platform that automates the deployment, scaling, and management of applications by using **containers**.

## Why do we need it?

### 1. "It works on my machine"
Docker eliminates environment inconsistency by ensuring the same setup is used by every developer and in production.

### 2. Isolation
Docker allows us to run multiple applications with conflicting requirements on the same machine without them interfering with each other.

### 3. Lightweight & Fast
Unlike Virtual Machines (VMs), Docker containers share the host machine's kernel, making them much faster and less resource-intensive.

## Popular Commands
Here are the commands you will use most often:

| Command | Description |
| :--- | :--- |
| `docker-compose up -d` | Start all services defined in `docker-compose.yaml`. |
| `docker-compose down` | Stop and remove all containers defined in the compose file. |
| `docker ps` | List all running containers. |
| `docker logs <name>` | See the output/logs of a container. |
| `docker exec -it <name> bash` | Open a terminal "inside" the container. |

## How we use it here
In this project, we use **Docker Compose** to manage two separate **TimescaleDB** instances for environment isolation.

### Service Mapping

| Environment | Port | Container Name | Persistent Volume |
| :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `timescaledb_data_dev` |
| **Production** | `5435` | `timescaledb-prod` | `timescaledb_data_prod` |

### Infrastructure Lifecycle
To start both database instances with persistent storage:
```bash
docker-compose up -d
```

To stop all instances without deleting data:
```bash
docker-compose stop
```

To stop and remove containers (data persists in volumes):
```bash
docker-compose down
```
