# Docker Overview

## What is Docker?
**Docker** is an open-source platform that automates the deployment, scaling, and management of applications by using **containers**.

Think of a container like a standardized shipping container in the real world. Just as a shipping container can hold anything from electronics to furniture and be moved by any ship, truck, or crane, a Docker container packages an application with all of its dependencies (code, runtime, system tools, libraries) into a single, consistent unit that can run on any machine.

## Why do we need it?

### 1. "It works on my machine"
The most common problem in software development is an app working on a developer's laptop but failing in production due to different versions of Python, databases, or operating system settings. Docker eliminates this by ensuring the environment is identical everywhere.

### 2. Isolation
Docker allows us to run multiple applications with conflicting requirements on the same machine without them interfering with each other. In this project, we run **TimescaleDB** in a container, keeping it separate from your system's main processes.

### 3. Lightweight & Fast
Unlike Virtual Machines (VMs), which require a full operating system, Docker containers share the host machine's kernel. This makes them much smaller, faster to start, and less resource-intensive.

### 4. Portability
A Dockerized application can be moved from a local laptop to a cloud provider (like AWS, Azure, or Google Cloud) or a local server with zero changes to the code.

## Global Adoption
Docker has become the industry standard for containerization:
- **Ubiquity**: Millions of developers and over 7 million applications are containerized using Docker.
- **Enterprise Use**: Over 70% of Fortune 500 companies use Docker in their tech stacks.
- **Cloud Standard**: Every major cloud provider has native support for Docker, making it the fundamental building block of modern "Cloud Native" architecture.

## How we use it here

### 1. Database Isolation
We use **Docker Compose** to run two independent **TimescaleDB** instances on different ports. This ensures that development data never bleeds into production.

| Environment | Port | Container Name | Persistent Volume |
| :--- | :--- | :--- | :--- |
| **Development** | `5434` | `timescaledb-dev` | `timescaledb_data_dev`, `parquet_data_dev` |
| **Production** | `5435` | `timescaledb-prod` | `timescaledb_data_prod`, `parquet_data_prod` |

**Startup Command**:
```bash
docker-compose up -d
```

### 2. High-Volume Data (Parquet)
High-volume analytical data is stored as Parquet files on the host machine (e.g., Google Drive) and mounted into the ETL containers at runtime.

-   **Host Path**: Defined by `DATA_DIR` in `.env` files.
-   **Container Path**: `/data`.
-   **Isolation**: Environment-specific subfolders (`data/dev` vs `data/prd`).

### 3. ETL Service Isolation
We build environment-specific images using the same `Dockerfile.etl`. By using build arguments, we bake the configuration directly into the image.

**Key Arguments**:
- `DB_PORT`: `5434` (Dev) vs `5435` (Prod).
- `ENV_PREFIX`: `dev` vs `prd`.

**Build Commands**:
- **Dev**: `npx nx run etl-service:docker-build:dev`
- **Prod**: `npx nx run etl-service:docker-build:prod`

## CI/CD Orchestration & Networking

### Shared Network
A dedicated Docker network, `enterprise-network`, facilitates secure communication between services:
- **Jenkins**: Performs builds and triggers deployments on this network.
- **Prefect Server**: Accessible at `http://prefect-server:4200/api` within the network.
- **Flow Run Containers**: Join this network to resolve `host.docker.internal` (DB) and `prefect-server`.

### Path Parity (Windows to Linux)
To ensure compatibility between Windows-based development hosts and Linux-based Docker containers, our orchestration logic automatically translates Windows drive letters (e.g., `G:/`) into Docker-compatible paths (e.g., `//g/`) during volume mounting.

### Advanced: Docker-in-Docker
The Jenkins container has access to the host's Docker engine via a socket mount (`/var/run/docker.sock`). This allows it to build, tag, and run the ETL images as part of the automated pipeline.

## Popular Commands
Here are the commands you will use most often:

| Command | Description |
| :--- | :--- |
| `docker ps` | List all running containers. |
| `docker ps -a` | List all containers (including stopped ones). |
| `docker logs <name>` | See the output/logs of a container. |
| `docker stop <name>` | Stop a running container. |
| `docker start <name>` | Start a stopped container. |
| `docker rm <name>` | Delete a container. |
| `docker volume ls` | List all persistent data volumes. |
| `docker exec -it <name> bash` | Open a terminal "inside" the container. |
