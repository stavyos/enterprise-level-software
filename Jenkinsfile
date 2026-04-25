node {
    def DEPLOY_ENV = ''
    def agentImage = null
    def appImage = null

    stage('Checkout') {
        checkout scm
    }

    stage('Set Environment') {
        if (env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'main' || env.BRANCH_NAME == null) {
            DEPLOY_ENV = 'prod'
        } else {
            DEPLOY_ENV = 'dev'
        }
        env.DEPLOY_ENV = DEPLOY_ENV
        echo "Target Environment: ${env.DEPLOY_ENV}"
    }

    stage('Prepare Agent') {
        echo "Building custom Jenkins agent image..."
        agentImage = docker.build("jenkins-agent-python", "-f Dockerfile.jenkins-agent .")
    }

    // Use the custom agent for a consistent build environment
    agentImage.inside("-u root") {
        stage('Cleanup') {
            echo "Cleaning up existing virtual environments..."
            sh "find . -name '.venv' -type d -exec rm -rf {} +"
        }

        stage('Setup') {
            echo "Installing Dependencies inside Docker..."
            sh "npm install"
            sh "npm run install:all"
        }

        stage('Tests') {
            echo "Running All Tests inside Docker..."
            // Provide dummy environment variables for Pydantic Settings validation during tests
            withEnv([
                'EODHD_API_KEY=dummy_key',
                'DB_USER=dummy_user',
                'DB_PASSWORD=dummy_pass',
                'DB_NAME=dummy_db'
            ]) {
                sh "npm run test:all"
            }
        }
    }

    stage('Build') {
        echo "Building Application Docker Image for ${env.DEPLOY_ENV}..."
        appImage = docker.build("etl-service:${env.DEPLOY_ENV}", "--build-arg ENV_PREFIX=${env.DEPLOY_ENV} -f Dockerfile.etl .")
    }

    stage('Deploy') {
        echo "Deploying Prefect Flows to ${env.DEPLOY_ENV}..."
        // Run the deployment command inside the newly built application image
        // This ensures uv and all python dependencies are available
        appImage.inside("-u root --add-host host.docker.internal:host-gateway") {
            dir('apps/etl-service') {
                // Use host.docker.internal to reach the Prefect server running on the host
                withEnv([
                    "ENV_PREFIX=${env.DEPLOY_ENV}",
                    "PREFECT_API_URL=http://host.docker.internal:4200/api"
                ]) {
                    sh "uv run python -c \"import asyncio; from etl_service.etl.deploy_etls import deploy; asyncio.run(deploy(image='etl-service:${env.DEPLOY_ENV}'))\""
                }
            }
        }
    }
}
