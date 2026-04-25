node {
    def DEPLOY_ENV = ''
    def agentImage = null
    def appImage = null

    try {
        stage('Checkout') {
            checkout scm
        }

        // Notify GitHub that the build is starting using the Default context source
        // This is more compatible across different GitHub plugin versions
        step([
            $class: 'GitHubCommitStatusSetter',
            contextSource: [$class: 'DefaultCommitContextSource'],
            statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: 'Build in progress', state: 'PENDING']]]
        ])

        stage('Set Environment') {
            echo "BRANCH_NAME: ${env.BRANCH_NAME}"
            echo "GIT_BRANCH: ${env.GIT_BRANCH}"

            def masterRegex = /^(.*\/)?master$/
            def isMaster = (env.BRANCH_NAME =~ masterRegex || env.GIT_BRANCH =~ masterRegex)

            if (isMaster) {
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
            appImage.inside("-u root --network enterprise-network") {
                dir('apps/etl-service') {
                    withEnv([
                        "ENV_PREFIX=${env.DEPLOY_ENV}",
                        "PREFECT_API_URL=http://prefect-server:4200/api"
                    ]) {
                        sh "uv run python -c \"import asyncio; from etl_service.etl.deploy_etls import deploy; asyncio.run(deploy(image='etl-service:${env.DEPLOY_ENV}'))\""
                    }
                }
            }
        }

        currentBuild.result = "SUCCESS"
    } catch (e) {
        currentBuild.result = "FAILURE"
        throw e
    } finally {
        // Notify GitHub of the final result using the Default context source
        try {
            def statusState = (currentBuild.result == 'SUCCESS') ? 'SUCCESS' : 'FAILURE'
            def statusMsg = (currentBuild.result == 'SUCCESS') ? 'Build successful' : 'Build failed'

            step([
                $class: 'GitHubCommitStatusSetter',
                contextSource: [$class: 'DefaultCommitContextSource'],
                statusResultSource: [$class: 'ConditionalStatusResultSource', results: [[$class: 'AnyBuildResult', message: statusMsg, state: statusState]]]
            ])
        } catch (statusError) {
            echo "Failed to set GitHub status: ${statusError.message}"
        }
    }
}
