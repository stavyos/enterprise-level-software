# Jenkins CI/CD

## Overview
This project uses Jenkins for continuous integration and deployment. The pipeline is defined in a scripted `Jenkinsfile` at the root of the repository.

## Automation Architecture
```mermaid
graph TD
    subgraph GitHub
        G[Repository]
        PR[Pull Request]
        CH[Status Checks]
    end

    subgraph "Local Network (via Ngrok)"
        subgraph "Jenkins (Docker Container)"
            JK[Pipeline]
            BL[Build Docker]
            DP[Deploy]
        end

        subgraph "Docker Shared Network"
            PS[Prefect Server]
            AG[Custom Build Agent]
        end
    end

    G -- "Push/PR Webhook" --> JK
    JK -- "Start Agent" --> AG
    AG -- "Tests & Setup" --> AG
    JK -- "Build ETL Image" --> BL
    BL -- "Register Flows" --> DP
    DP -- "API Calls" --> PS
    JK -- "Report Results" --> CH
```

## Jenkins UI
Jenkins provides a web-based interface for managing builds and visualizing pipelines.
*   **Standard View**: Accessible via the main Jenkins URL (default: `http://localhost:8080`).
*   **Blue Ocean**: A modern, interactive visualization of the pipeline stages and logs.

## How to Start Jenkins (Docker Compose)
The project includes a `docker-compose.yaml` file that orchestrates Jenkins along with the TimescaleDB instances. This ensures all services are on the same `enterprise-network` and can communicate easily.

To start Jenkins and the databases:
```bash
docker-compose up -d
```

This configuration includes:
*   **Docker-in-Docker**: The Docker socket is mounted (`/var/run/docker.sock`) so Jenkins can build and run project-specific images.
*   **Persistence**: A volume named `jenkins_home` preserves your jobs, plugins, and configuration.
*   **Networking**: All services share the `enterprise-network`.

**Note for Windows users**: Ensure Docker Desktop is running.

Once started:
1.  Navigate to `http://localhost:8080`.
2.  Retrieve the initial admin password: `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword`.
3.  **Setup Wizard**: Select **"Install suggested plugins"**. This includes essential plugins for this project:
    *   **Pipeline**: Core engine for `Jenkinsfile` execution.
    *   **Git**: For source code management.
    *   **Docker Pipeline**: Required for `docker.image().inside` and containerized stages.
4.  Create your first admin user.

## Advanced: Multibranch Pipelines (Automatic PR Jobs)
Multibranch Pipelines provide isolation for each branch and PR, automatic discovery of new feature branches and pull requests, and automatic cleanup of jobs when branches are deleted.

### Configuration (Final Stable Setup)
To bypass GitHub API rate limits (60/hr anonymous) and ensure reliable discovery, this project uses the standard **Git** source type instead of the GitHub-specific source.

1.  **Create New Item**: Select **Multibranch Pipeline**.
2.  **Branch Sources**:
    *   Add source: **Git**.
    *   **Project Repository**: `https://github.com/stavyos/enterprise-level-software.git`.
    *   **Credentials**: Select `github-token`.
    *   **Traits**: Ensure **"Discover branches"** is added (required for the Git source to see branches).
3.  **Scan Triggers**: Set to **1 minute**.

### Concurrency Control (Single Build Only)
To prevent build collisions and ensure stability in our local environment, Jenkins is configured to run only **one build at a time** across all projects.
*   **Implementation**: The number of executors on the "Built-in Node" is set to **1**.
*   **Effect**: If multiple PRs are pushed simultaneously, they will wait in the queue and run sequentially.

### Manual Recovery/Setup
If you need to recreate the job or fix authentication:
1.  **Link Credentials**: Ensure your GitHub PAT is added as `github-token` (Secret Text) in **Manage Jenkins > Credentials**.
2.  **Verify Git Plugin**: Ensure the "Git" plugin is installed and updated.
3.  **Force Scan**: Click **"Scan Multibranch Pipeline Now"** inside the project to refresh the branch list.

### Replication Guide: Setting up Stable PR Jobs
If you need to set up this system in a new Jenkins instance, follow these exact steps to avoid the common pitfalls (like rate-limiting) we encountered:

1.  **Inject Credentials**:
    *   Retrieve your GitHub PAT.
    *   Add it to Jenkins as a **Secret Text** credential with the ID `github-token`.
2.  **Disable Parallelism**:
    *   Go to **Manage Jenkins > Nodes**.
    *   Click on **(built-in)** > **Configure**.
    *   Set **Number of executors** to `1`. This ensures builds run sequentially and prevents Docker resource collisions.
3.  **Create the Multibranch Job**:
    *   **New Item** > **Multibranch Pipeline**.
    *   **Branch Sources**: Choose **Git** (NOT GitHub).
    *   **Project Repository**: `https://github.com/stavyos/enterprise-level-software.git`.
    *   **Credentials**: Select `github-token`.
    *   **Traits**: You MUST add **"Discover branches"** from the traits list, or the Git source will see nothing.
4.  **Automatic Scanning**:
    *   Under **Scan Multibranch Pipeline Triggers**, check "Periodically if not otherwise run" and set it to **1 minute**.
5.  **Verification**:
    *   Click **Save**.
    *   Click **Scan Multibranch Pipeline Now** on the sidebar.
    *   Check the **Scan Multibranch Pipeline Log**; it should show "Finished: SUCCESS" and list your branches.

### Troubleshooting & Maintenance

#### 1. GitHub API Rate Limiting (Builds Stuck)
If the "Branch Indexing" or builds appear stuck, Jenkins may be rate-limited by GitHub (especially for anonymous requests).
*   **Symptom**: Logs show `Jenkins-Imposed API Limiter: ... Sleeping`.
*   **Fix**: Ensure a valid `github-token` credential of type "Secret Text" exists and is associated with the Multibranch project.
*   **Strategy**: In **Manage Jenkins > System > GitHub API usage**, set the rate limit strategy to **"Throttle at end"** or **"Throttle on over"** to prevent proactive sleeping.

#### 2. Updating the GitHub Token
If your local or injected token expires:
1.  Generate a new PAT in GitHub.
2.  In Jenkins, go to **Manage Credentials > Global > github-token**.
3.  Update the "Secret" with your new PAT and save.
4.  Trigger a "Scan Multibranch Pipeline Now" on the job to refresh branch indexing.

## Configuring the Pipeline Job
Once logged in, follow these steps to link your repository to Jenkins:

1.  **Create New Item**: Click "New Item" on the sidebar.
2.  **Item Name**: Enter a name (e.g., `enterprise-level-software`).
3.  **Type**: Select **Pipeline** and click OK.
4.  **Pipeline Configuration**:
    *   Scroll down to the **Pipeline** section.
    *   **Definition**: Select **Pipeline script from SCM**.
    *   **SCM**: Select **Git**.
    *   **Repository URL**: Enter your local path or GitHub URL.
    *   **Branch Specifier**: Use `*/master` for production or `*/sy/jenkins-cicd` to test this PR.
    *   **Script Path**: Ensure it is set to `Jenkinsfile`.
5.  **Save**: Click Save.
6.  **Run**: Click **Build Now** on the left sidebar to trigger your first build!

## Connecting Jenkins to GitHub (Local to Cloud)
To allow GitHub to trigger builds and display status checks from your local Jenkins instance, follow these steps:

### 1. Expose Jenkins via Ngrok Tunnel
Since GitHub is on the public cloud, use **Ngrok** to create a secure tunnel:
1.  **Auth**: Run `ngrok config add-authtoken <TOKEN>`.
2.  **Start Tunnel**: Run `ngrok http 8080`.
3.  **Forwarding URL**: Copy the forwarded URL (e.g., `<NGROK_URL>`).

### 2. Configure GitHub Webhook
1.  In your GitHub Repo: **Settings > Webhooks > Add Webhook**.
2.  **Payload URL**: `<NGROK_URL>/github-webhook/` (The `/github-webhook/` suffix is mandatory).
3.  **Content type**: `application/json`.
4.  **Events**: Select **Let me select individual events** and check **Pushes** and **Pull requests**.

### 3. Enable Jenkins Triggers
To allow Jenkins to listen for these webhooks:
1.  **Jenkins URL**: In **Manage Jenkins > System**, set the **Jenkins URL** to your Ngrok URL.
2.  **Job Trigger**: In your Pipeline job configuration, under **Build Triggers**, check **"GitHub hook trigger for GITScm polling"**.

### 4. Enable GitHub Status Checks
To see build results (Success/Failure) directly on your GitHub PRs:
1.  **Install Plugin**: Ensure the **GitHub Integration** plugin is installed in Jenkins.
2.  **Credentials**: Add a GitHub Personal Access Token (PAT) as a "Secret text" credential named `github-token`.
3.  **Global Config**: In **Manage Jenkins > System**, add a GitHub Server, select the `github-token`, and click "Test Connection".
4.  **Pipeline Implementation**: The `Jenkinsfile` uses the `GitHubCommitStatusSetter` step to report status:
    *   **Pending**: Reported after checkout.
    *   **Final Result**: Reported in the `finally` block based on the build outcome (`SUCCESS` or `FAILURE`).

## Pipeline Structure
The pipeline uses **Dockerized Stages** and **Automated Status Reporting**:

1.  **Set Environment**: Runs on the host; determines `dev` or `prod` based on the branch.
    *   **Master Detection**: Uses a precise regex `^(.*/)?master$` to match only the `master` branch.
    *   **Fallback**: All other branches (PRs, features) default to the `dev` environment.
2.  **Status Check (Universal)**: Reports a "Pending" status to GitHub once the build starts.
3.  **Setup & Tests (Dockerized)**: These stages run inside a custom agent image (`jenkins-agent-python`).
    *   Ensures that Node.js, npm, Nx, and `uv` commands run in a Linux environment.
4.  **Build**: Builds the environment-specific application image on the host.
5.  **Deploy**: Runs flow registration **inside** the newly built application image. It uses a specialized deployment script that strips environment-specific metadata (like local paths) to ensure the registered flows are portable across any Docker host.
6.  **Final Status**: Reports the final Success/Failure to GitHub.
## Environment Isolation
Isolation between `dev` and `prod` is maintained through:
*   **Docker Tags**: Environment-specific images (`etl-service:dev`, `etl-service:prod`).
*   **Env Prefix**: Used to distinguish deployments and flows in the Prefect UI.
*   **Configuration**: Environment-specific `.env` files (loaded during runtime in the container or via `ENV_PREFIX` during deployment).
*   **Templates**: `template.dev.env` and `template.prod.env` provide the structure for environment-specific configuration.

## Requirements
*   Jenkins with `Pipeline` plugin.
*   Node.js and npm installed on the Jenkins runner.
*   `uv` installed and available in the PATH.
*   Docker installed and accessible by the Jenkins user.
*   Prefect server accessible from the Jenkins runner.
