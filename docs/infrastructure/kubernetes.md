# Kubernetes (K8s)

## Overview
Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. In this project, it serves as the foundational infrastructure for executing distributed ETL flows.

## Why We Need It
- **Scalability**: K8s allows us to scale our ETL workers horizontally based on the volume of data.
- **Resilience**: If a node or a job fails, K8s automatically handles the lifecycle, and Prefect can leverage this to retry flows.
- **Resource Management**: We can precisely define CPU and Memory requirements for each ETL task.

## Main Concepts
| Concept | Description |
| :--- | :--- |
| **Node** | A physical or virtual machine that runs containers. |
| **Pod** | The smallest deployable unit in K8s. It contains one or more containers (e.g., our `etl-service` container). |
| **Job** | A controller that creates one or more Pods and ensures they successfully terminate. **Our Prefect flows run as K8s Jobs.** |
| **Work Pool** | (Prefect Specific) A bridge between Prefect and K8s that submits Job specifications to the cluster. |
| **Namespace** | A logical isolation within a cluster. |

## Environment Specific Infrastructure

We use separate namespaces and work pools to ensure isolated execution between development and production environments.

| Environment | Work Pool Name | Target Namespace | Target Cluster |
| :--- | :--- | :--- | :--- |
| **Development** | `dev-k8s-pool` | `dev` | `docker-desktop` |
| **Production** | `prod-k8s-pool` | `prod` | `docker-desktop` |

### Resource Mapping
We define resources in `etl/deployments_settings/job_variables.py`:
- **Requests**: Minimum resources guaranteed to the pod.
- **Limits**: Maximum resources the pod is allowed to consume.

### Example configuration
```python
job_variables = {
    "requests": {"cpu": "1000m", "memory": "2Gi"},
    "limits": {"cpu": "2000m", "memory": "4Gi"},
    "pod_watch_timeout_seconds": 3600
}
```

## Local Development
For local testing, we typically use **Docker Desktop (K8s enabled)** to simulate the cluster environment. Ensure your context is correctly set:
```powershell
kubectl config use-context docker-desktop
```
