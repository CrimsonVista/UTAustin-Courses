pipeline { 
    agent any 
    stages {
        stage('Build') { 
            steps { 
                sh '''#!/bin/bash
                pwd
                echo copying tests to git repo
                cp /u/srolo/netsec-tests/test1.py $(pwd)/newsapp/newslister/tests.py
                '''
            }
        }
        
        stage('Submit Check'){
            steps {
                script {
                    try{
                        sh 'ls submit.txt'
                        echo "Submission mode activated"}
                    catch(err){
                        echo "Submission mode not activated"
                        currentBuild.result = 'ABORTED' }
                }
            }
        }
        
        stage('Test'){
            when {expression{currentBuild.result != 'ABORTED'}}
            steps {
                sh 'echo test phase'
                script{
                    try{
                        withEnv(['PATH+JENKINSHOME=/u/srolo/.local/bin']) {
                            sh '''#!/bin/bash
                            cd newsapp
                            pipenv install django
                            pipenv run pip install newsapi-python
                            pipenv run pip install cryptography
                            pipenv run python generate_secret.py
                            pipenv run python manage.py migrate --run-syncdb
                            pipenv run python manage.py test || exit -1
                            ls
                            '''
                            
                        }
                        currentBuild.result = 'SUCCESS'
                        sh 'cat newsapp/result.txt'
                        sh '''#!/bin/bash
                        mail -s "Lab 1 Test Passed" ishanphadke@utexas.edu < newsapp/result.txt
                        '''
                    }
                    catch(Exception e){
                        currentBuild.result = 'FAILURE'
                        sh 'cat newsapp/result.txt'
                        sh '''#!/bin/bash
                        mail -s "Lab 1 Test Failed" ishanphadke@utexas.edu < newsapp/result.txt
                        '''
                    }
                }
            }
        }
    }
}
