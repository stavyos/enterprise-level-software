# Kubernetes (K8s)

## Overview
Kubernetes serves as the foundational infrastructure for executing our distributed ETL flows as containerized Jobs.

## Shared Infrastructure Strategy
To reduce local overhead, we use a **single shared Kubernetes cluster** and a unified Prefect work pool.

| Component | Shared Resource |
| :--- | :--- |
| **Work Pool Name** | `my-k8s-pool` |
| **Execution Context** | `docker-desktop` |

### Isolated Execution
Although the cluster is shared, execution is isolated through Docker images:
1.  **Job Dispatch**: Prefect dispatches a Job to the cluster.
2.  **Image Selection**: The Job uses either `etl-service:dev` or `etl-service:prod`.
3.  **Baked Config**: The image itself contains the correct routing logic to connect to the isolated database instances.

## Resource Management
We define resources in `etl/deployments_settings/job_variables.py` to ensure workers have sufficient CPU and Memory.

```python
job_variables = {
    "requests": {"cpu": "1000m", "memory": "2Gi"},
    "limits": {"cpu": "2000m", "memory": "4Gi"}
}
```
