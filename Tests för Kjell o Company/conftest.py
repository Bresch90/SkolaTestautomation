def pytest_addoption(parser):
    parser.addoption(
        '--browser', action='store', default='firefox', help='Browser to test. Chrome, firefox, edge. Default is Chrome.'
    )