node {
    def DEPLOY_ENV = ''

    stage('Set Environment') {
        // Simple logic can run on the host agent
        if (env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'main') {
            DEPLOY_ENV = 'prod'
        } else {
            DEPLOY_ENV = 'dev'
        }
        env.DEPLOY_ENV = DEPLOY_ENV
        echo "Target Environment: ${env.DEPLOY_ENV}"
    }

    // Use a Docker container for a consistent build environment
    // We'll use a custom image or a node image that can handle our needs
    docker.image('node:20-slim').inside {
        stage('Setup') {
            echo "Installing Dependencies inside Docker..."
            // Inside the Linux-based container, we use 'sh' instead of 'bat'
            sh "npm install"
            sh "npm run install:all"
        }

        stage('Tests') {
            echo "Running All Tests inside Docker..."
            sh "npm run test:all"
        }
    }

    stage('Build') {
        echo "Building Application Docker Image for ${env.DEPLOY_ENV}..."
        // Building images requires access to the host's Docker daemon
        // This part usually runs on the host agent (outside the 'inside' block)
        if (isUnix()) {
            sh "docker build --build-arg ENV_PREFIX=${env.DEPLOY_ENV} -f Dockerfile.etl -t etl-service:${env.DEPLOY_ENV} ."
        } else {
            bat "docker build --build-arg ENV_PREFIX=${env.DEPLOY_ENV} -f Dockerfile.etl -t etl-service:${env.DEPLOY_ENV} ."
        }
    }

    stage('Deploy') {
        echo "Deploying Prefect Flows to ${env.DEPLOY_ENV}..."
        // Deploying also uses the host tools to interact with the Prefect server
        dir('apps/etl-service') {
            withEnv(["ENV_PREFIX=${env.DEPLOY_ENV}"]) {
                if (isUnix()) {
                    sh "uv run python -c \"from etl_service.etl.deploy_etls import deploy; deploy(image='etl-service:${env.DEPLOY_ENV}')\""
                } else {
                    bat "uv run python -c \"from etl_service.etl.deploy_etls import deploy; deploy(image='etl-service:${env.DEPLOY_ENV}')\""
                }
            }
        }
    }
}
