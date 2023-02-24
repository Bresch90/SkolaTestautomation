chcp 1252
pytest --capture=no --log-cli-level=INFO --tb=short --browser=chrome .\\"Tests för Kjell o Company"\test_Kjell.py
pytest --capture=no --log-cli-level=INFO --tb=short --browser=firefox .\\"Tests för Kjell o Company"\test_Kjell.py
pytest --capture=no --log-cli-level=INFO --tb=short --browser=edge .\\"Tests för Kjell o Company"\test_Kjell.py
@echo Tests done!
pause
