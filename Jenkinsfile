// Jenkins pipeline för test av www.kjell.com med selenium
pipeline {
    agent any
    stages {

        stage ('SkolaTestAutomation - Chrome tests') {
            steps{
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE'){
                    bat encoding: 'UTF-8', script: """
                    chcp 65001
                    pytest -s --tb=short --log-cli-level=INFO --browser=chrome ".\\Tests för Kjell o Company\\test_Kjell.py"
                    @echo Chrome tests done!
                     """
                }
            }
        }

        stage ('SkolaTestAutomation - Firefox tests') {
            steps{
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE'){
                    bat encoding: 'UTF-8', script: """
                    chcp 65001
                    pytest -s --tb=short --log-cli-level=INFO --browser=firefox ".\\Tests för Kjell o Company\\test_Kjell.py"
                    @echo Firefox tests done!
                     """
                }
            }
        }

        stage ('SkolaTestAutomation - Edge tests') {
            steps{
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE'){
                    bat encoding: 'UTF-8', script: """
                    chcp 65001
                    pytest -s --tb=short --log-cli-level=INFO --browser=edge ".\\Tests för Kjell o Company\\test_Kjell.py"
                    @echo Edge tests done!
                     """
                }
            }
        }

        stage ('Cleaning Workspace'){
            steps {
                cleanWs()
            }
        }
	}
}
