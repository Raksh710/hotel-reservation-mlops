 pipeline{
    agent any

    environment {
        VENV_DIR = 'venv'

    }

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                echo 'Cloning Github repo to Jenkins.......'
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-jenkins-token', url: 'https://github.com/Raksh710/hotel-reservation-mlops.git']])
            }

            
        }

        stage('Setting up our Virtual Environment and Installing dependencies'){
            steps{
                echo 'Setting up our Virtual Environment and Installing dependencies'
                sh '''
                python -m venv ${VENV_DIR}
                ${VENV_DIR}/bin/activate
                pip install --upgrade pip
                pip install -e .
                '''
               
            }

            
        }
    }
 }