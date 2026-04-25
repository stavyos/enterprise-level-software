node {
    def DEPLOY_ENV = ''

    stage('Set Environment') {
        // Detect environment based on branch
        // master/main -> prod, otherwise -> dev
        if (env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'main') {
            DEPLOY_ENV = 'prod'
        } else {
            DEPLOY_ENV = 'dev'
        }
        env.DEPLOY_ENV = DEPLOY_ENV
        echo "Target Environment: ${env.DEPLOY_ENV}"
    }

    stage('Setup') {
        echo "Installing Dependencies..."
        // Use bat for Windows runner
        bat "npm install"
        bat "npm run install:all"
    }

    stage('Tests') {
        echo "Running All Tests..."
        bat "npm run test:all"
    }

    stage('Build') {
        echo "Building Docker Image for ${env.DEPLOY_ENV}..."
        bat "docker build --build-arg ENV_PREFIX=${env.DEPLOY_ENV} -f Dockerfile.etl -t etl-service:${env.DEPLOY_ENV} ."
    }

    stage('Deploy') {
        echo "Deploying Prefect Flows to ${env.DEPLOY_ENV}..."
        // Execute from the etl-service directory to ensure uv find the right pyproject.toml
        dir('apps/etl-service') {
            withEnv(["ENV_PREFIX=${env.DEPLOY_ENV}"]) {
                bat "uv run python -c \"from etl_service.etl.deploy_etls import deploy; deploy(image='etl-service:${env.DEPLOY_ENV}')\""
            }
        }
    }
}
