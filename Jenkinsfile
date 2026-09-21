pipeline {
    agent any

    environment {
        VENV_DIR    = 'venv'
        GCP_PROJECT = 'stellar-river-411501'
    }

    stages {
        stage('Cloning Github repo to Jenkins') {
            steps {
                echo 'Cloning Github repo to Jenkins.......'
                checkout scmGit(
                    branches: [[name: '*/main']],
                    extensions: [],
                    userRemoteConfigs: [[
                        credentialsId: 'github-jenkins-token',
                        url: 'https://github.com/Raksh710/hotel-reservation-mlops.git'
                    ]]
                )
            }
        }

        stage('Setting up our Virtual Environment and Installing dependencies') {
            steps {
                echo 'Setting up our Virtual Environment and Installing dependencies'
                sh '''
                python -m venv ${VENV_DIR}
                . ${VENV_DIR}/bin/activate
                pip install --upgrade pip
                pip install -e .
                '''
            }
        }

        stage('Building and Pushing Docker Image to GCR') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Building and Pushing Docker Image to GCR'
                        sh '''
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker gcr.io --quiet

                        docker build -t gcr.io/${GCP_PROJECT}/hotel-reservation-project:latest .
                        docker push gcr.io/${GCP_PROJECT}/hotel-reservation-project:latest
                        '''
                    }
                }
            }
        }
    }
}