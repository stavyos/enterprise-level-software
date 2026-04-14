pipeline {
    agent any

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['DEV', 'PROD'], description: 'Select the environment to deploy to')
    }

    environment {
        // We'll set the environment variables based on the selected parameter in the 'Set Environment' stage
        PREFECT_API_URL = ''
        DOCKER_TAG = ''
    }

    stages {
        stage('Set Environment') {
            steps {
                script {
                    if (params.ENVIRONMENT == 'DEV') {
                        env.PREFECT_API_URL = 'http://127.0.0.1:4200/api'
                        env.DOCKER_TAG = 'dev'
                        env.ENV_FILE = '.env.dev'
                    } else {
                        env.PREFECT_API_URL = 'http://127.0.0.1:4201/api'
                        env.DOCKER_TAG = 'prod'
                        env.ENV_FILE = '.env.prod'
                    }
                    echo "Environment set to: ${params.ENVIRONMENT}"
                    echo "Prefect API URL: ${env.PREFECT_API_URL}"
                    echo "Docker Tag: ${env.DOCKER_TAG}"
                }
            }
        }

        stage('Setup') {
            steps {
                script {
                    echo "Installing Node.js dependencies..."
                    bat "npm install"
                    echo "Installing project dependencies using Nx..."
                    bat "npx nx run-many -t install"
                    echo "Running code quality checks with ruff..."
                    // Assuming ruff is integrated into nx lint or run directly
                    bat "uv run ruff check ."
                }
            }
        }

        stage('Tests') {
            steps {
                script {
                    echo "Running tests for each app in the monorepo..."
                    bat "npx nx run-many -t test"
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    echo "Building Docker image with tag: ${env.DOCKER_TAG}..."
                    // We modify the docker-build command to use the environment-specific tag
                    bat "docker build -t etl-service:${env.DOCKER_TAG} -f Dockerfile.etl ."
                }
            }
        }

        stage('Publish') {
            steps {
                script {
                    echo "Placeholder for pushing image to remote ECR..."
                    // echo "docker push your-repo-url/etl-service:${env.DOCKER_TAG}"
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    echo "Deploying Prefect deployments to ${params.ENVIRONMENT} environment..."
                    // We need to ensure the correct environment file is used during deployment registration
                    // This might require the etl-service:deploy command to be aware of the environment
                    bat "uv run dotenv -f ${env.ENV_FILE} run -- npx nx run etl-service:deploy"
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline completed for ${params.ENVIRONMENT} environment."
        }
        success {
            echo "CI/CD process successful!"
        }
        failure {
            echo "CI/CD process failed. Please check logs."
        }
    }
}
