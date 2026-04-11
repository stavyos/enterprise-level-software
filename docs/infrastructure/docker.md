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

## How we use it here
In this project, we use Docker to provide a ready-to-use **TimescaleDB** instance. Instead of requiring you to manually install and configure PostgreSQL and the Timescale extension on your OS, you simply run one command, and Docker handles the rest.
