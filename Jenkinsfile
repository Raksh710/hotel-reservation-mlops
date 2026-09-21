pipeline {
    agent any

    environment {
        VENV_DIR     = 'venv'
        GCP_PROJECT  = 'stellar-river-411501'
        GCP_REGION   = 'us-central1'
        SERVICE_NAME = 'hotel-reservation-project'
        IMAGE        = "gcr.io/stellar-river-411501/hotel-reservation-project:latest"
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
                        export DOCKER_BUILDKIT=1

                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}
                        gcloud auth configure-docker gcr.io --quiet

                        docker build \
                          --secret id=gcp_key,src=${GOOGLE_APPLICATION_CREDENTIALS} \
                          -t ${IMAGE} .

                        docker push ${IMAGE}
                        '''
                    }
                }
            }
        }

        stage('Deploy to Google Cloud Run') {
            steps {
                withCredentials([file(credentialsId: 'gcp-key', variable: 'GOOGLE_APPLICATION_CREDENTIALS')]) {
                    script {
                        echo 'Deploying to Google Cloud Run'
                        sh '''
                        gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
                        gcloud config set project ${GCP_PROJECT}

                        gcloud run deploy ${SERVICE_NAME} \
                          --image ${IMAGE} \
                          --platform managed \
                          --region ${GCP_REGION} \
                          --port 5000 \
                          --memory 1Gi \
                          --allow-unauthenticated \
                          --quiet

                        echo "Service URL:"
                        gcloud run services describe ${SERVICE_NAME} \
                          --region ${GCP_REGION} \
                          --format 'value(status.url)'
                        '''
                    }
                }
            }
        }
    }
}