# Kubernetes (K8s)

## Overview
Kubernetes is used in this project as the foundational infrastructure for executing distributed ETL flows.

## Environment Architecture
We use a **single Kubernetes cluster** and work pool for both environments. Isolation is maintained at the application level through database separation and Prefect deployment prefixing.

| Component | Shared Resource |
| :--- | :--- |
| **Work Pool Name** | `my-k8s-pool` |
| **Target Cluster** | `docker-desktop` |

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
