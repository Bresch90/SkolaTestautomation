chcp 1252
pytest -s --tb=short --browser=chrome .\\"Tests för Kjell o Company"\test_Kjell.py
pytest -s --tb=short --browser=firefox .\\"Tests för Kjell o Company"\test_Kjell.py
pytest -s --tb=short --browser=edge .\\"Tests för Kjell o Company"\test_Kjell.py
@echo Tests done!
