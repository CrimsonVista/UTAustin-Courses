pipeline { 
    agent any 
    options {
        skipStagesAfterUnstable()
    }
    
    stages {
        stage('Build') { 
            steps { 
                sh 'echo copying tests to git repo' 
                sh 'cp /u/srolo/netsec-tests/test1.py /u/srolo/.jenkins/workspace/testpipe/newsapp/newslister/test.py'
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
                        currentBuild.result = 'FAILURE' }
                }
            }
        }
        
        stage('Test'){
            steps {
                sh 'echo test phase'
                script{
                    try{
                        withEnv(['PATH+JENKINSHOME=/u/srolo/.local/bin']) {
                            sh '''
                            cd newsapp
                            pipenv install django
                            pipenv run pip install newsapi-python
                            pipenv run pip install cryptography
                            pipenv run python generate_secret.py
                            pipenv run python manage.py test
                            ls
                            '''
                        }
                        sh 'cat newsapp/result.txt'
                        sh '''#!/bin/bash
                        mail -s "Lab 1 Test Passed" <ishanphadke@utexas.edu> < newsapp/result.txt
                        '''
                    }
                    catch(err){
                        currentBuild.result = 'FAILURE'
                        sh '''#!/bin/bash
                        mail -s "Lab 1 Test Failed" <put your email address here> < newsapp/result.txt
                        '''
                    }
                }
            }
        }
    }
}
