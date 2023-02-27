// Jenkins pipeline för test av www.kjell.com med selenium
pipeline {
    agent any
    stages {
        stage ('SkolaTestAutomation - Checkout') {
            steps{
                checkout([$class: 'GitSCM', branches: [[name: '**']], doGenerateSubmoduleConfigurations: false,
                 extensions: [], submoduleCfg: [],
                  userRemoteConfigs: [[credentialsId: '', url: 'https://github.com/Bresch90/SkolaTestautomation.git']]])
            }
        }

        stage ('SkolaTestAutomation - Chrome tests') {
            steps{
                cleanWs()
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE'){
                    bat encoding: 'UTF-8', script: """
                    chcp 65001
                    c:
                    cd C:\\Users\\Alex\\Documents\\Skola\\"Kurs 5 Testautomation"\\SkolaTestautomation
                    pytest -s --tb=short --log-cli-level=INFO --browser=chrome ".\\Tests för Kjell o Company\\test_Kjell.py"
                    @echo Chrome tests done!
                     """
                }
            }
        }

        stage ('SkolaTestAutomation - Firefox tests') {
            steps{
                cleanWs()
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE'){
                    bat encoding: 'UTF-8', script: """
                    chcp 65001
                    c:
                    cd C:\\Users\\Alex\\Documents\\Skola\\"Kurs 5 Testautomation"\\SkolaTestautomation
                    pytest -s --tb=short --log-cli-level=INFO --browser=firefox ".\\Tests för Kjell o Company\\test_Kjell.py"
                    @echo Firefox tests done!
                     """
                }
            }
        }

        stage ('SkolaTestAutomation - Edge tests') {
            steps{
                cleanWs()
                catchError(buildResult: 'FAILURE', stageResult: 'FAILURE'){
                    bat encoding: 'UTF-8', script: """
                    chcp 65001
                    c:
                    cd C:\\Users\\Alex\\Documents\\Skola\\"Kurs 5 Testautomation"\\SkolaTestautomation
                    pytest -s --tb=short --log-cli-level=INFO --browser=edge ".\\Tests för Kjell o Company\\test_Kjell.py"
                    @echo Edge tests done!
                     """
                }
            }
        }
	}
}
