 pipeline{
    agent any

    stages{
        stage('Cloning Github repo to Jenkins'){
            steps{
                echo 'Cloning Github repo to Jenkins.......'
                checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-jenkins-token', url: 'https://github.com/Raksh710/hotel-reservation-mlops.git']])
            }
        }
    }
 }