node {
    def DEPLOY_ENV = ''
    def agentImage = null

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
    agentImage.inside {
        stage('Setup') {
            echo "Installing Dependencies inside Docker..."
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
        if (isUnix()) {
            sh "docker build --build-arg ENV_PREFIX=${env.DEPLOY_ENV} -f Dockerfile.etl -t etl-service:${env.DEPLOY_ENV} ."
        } else {
            bat "docker build --build-arg ENV_PREFIX=${env.DEPLOY_ENV} -f Dockerfile.etl -t etl-service:${env.DEPLOY_ENV} ."
        }
    }

    stage('Deploy') {
        echo "Deploying Prefect Flows to ${env.DEPLOY_ENV}..."
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
