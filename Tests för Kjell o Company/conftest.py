def pytest_addoption(parser):
    parser.addoption(
        '--browser', action='store', default='chrome', help='Browser to test. Chrome, firefox, edge. Default is Chrome.'
    )
    parser.addoption(
        '--headless', action='store', default='False', help='Running tests headless or not'
    )
