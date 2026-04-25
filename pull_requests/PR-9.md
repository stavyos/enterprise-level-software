# PR-9: Multi-Environment Jenkins CI/CD Implementation

## Purpose
Implement a robust, scripted Jenkins CI/CD pipeline that supports multiple environments (Dev/Prod). This PR introduces automated branch detection, environment-specific Docker builds, and Prefect flow registration, ensuring that every commit and PR is verified and deployed correctly.

## Reviewer Reading Guide
1. **`Jenkinsfile`**: Review the scripted pipeline logic, especially the environment detection and stage definitions.
2. **`docs/infrastructure/jenkins.md`**: Check the new documentation for clarity and completeness.

## Key Changes

### 1. Scripted Jenkins Pipeline
- Implemented `Jenkinsfile` using Groovy scripting.
- Added **Set Environment** stage for automatic branch-to-environment mapping (`master`/`main` -> `prod`, others -> `dev`).
- Integrated **Setup** stage using `npm` and `uv` for monorepo-wide dependency management.
- Added **Tests** stage executing `nx run-many -t test`.
- Implemented **Build** stage using environment-specific Docker tags and build-args.
- Added **Deploy** stage for automated Prefect flow registration with environment isolation.

### 2. Infrastructure Documentation
- Created `docs/infrastructure/jenkins.md` in the Tech Learning Center.
- Documented pipeline stages, environment isolation strategy, and runner requirements.

## Architecture & Dependency Graph
```mermaid
graph TD
    subgraph Jenkins
        P[Pipeline]
    end
    subgraph Environments
        D[Dev Environment]
        PR[Prod Environment]
    end
    P -- "Branch != master" --> D
    P -- "Branch == master" --> PR

    subgraph Stages
        S1[Set Environment]
        S2[Setup]
        S3[Tests]
        S4[Build Docker]
        S5[Deploy Prefect]
    end

    P --> S1
    S1 --> S2
    S2 --> S3
    S3 --> S4
    S4 --> S5
```

## Date
Saturday, April 25, 2026
