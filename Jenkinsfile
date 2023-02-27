// Powered by Infostretch 

timestamps {

    node () {

        stage ('SkolaTestAutomation - Checkout') {
         checkout([$class: 'GitSCM', branches: [[name: '**']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: '', url: 'https://github.com/Bresch90/SkolaTestautomation.git']]])
        }
        stage ('SkolaTestAutomation - Test') {
                // Batch build step
            bat """
                chcp 1252
                c:
                cd C:\\Users\\Alex\\Documents\\Skola\\"Kurs 5 Testautomation"\\SkolaTestautomation
                pytest -s --tb=short --log-cli-level=INFO --browser=chrome .\\"Tests för Kjell o Company"\\test_Kjell.py
                @echo Chrome tests done!
             """
                // Batch build step
            bat """
                chcp 1252
                c:
                cd C:\\Users\\Alex\\Documents\\Skola\\"Kurs 5 Testautomation"\\SkolaTestautomation
                pytest -s --tb=short --log-cli-level=INFO --browser=firefox .\\"Tests för Kjell o Company"\\test_Kjell.py
                @echo Firefox tests done!
             """
                // Batch build step
            bat """
                chcp 1252
                c:
                cd C:\\Users\\Alex\\Documents\\Skola\\"Kurs 5 Testautomation"\\SkolaTestautomation
                pytest -s --tb=short --log-cli-level=INFO --browser=edge .\\"Tests för Kjell o Company"\\test_Kjell.py
                @echo Edge tests done!
             """
        }
    }
}