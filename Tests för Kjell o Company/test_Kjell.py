from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
import pytest
from time import sleep

HOMEPAGE = "https://www.kjell.com/se/"
browser = 'chrome'


@pytest.fixture(autouse=True, scope='class')
def driver(request):
    global browser
    browser = request.config.getoption('--browser').lower()

    match browser:
        case "chrome":
            from webdriver_manager.chrome import ChromeDriverManager
            from selenium.webdriver.chrome.service import Service
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        case "firefox":
            from webdriver_manager.firefox import GeckoDriverManager
            from selenium.webdriver.firefox.service import Service
            driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

        case "edge":
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            from selenium.webdriver.edge.service import Service
            driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()))

        case _:
            raise ValueError(f"Bad input from --browser variable [{browser}]. Did you misspell it?")

    yield driver
    driver.quit()


class TestKjell:
    def wait_and_click(self, active_driver, path):
        WebDriverWait(active_driver, timeout=5).until(lambda d: d.find_element(By.XPATH, path))
        element = active_driver.find_element(By.XPATH, path)
        element.click()

    def test_open_homepage(self, driver):
        driver.get(HOMEPAGE)
        assert "Kjell" in driver.title

    def test_search_bar(self, driver):
        driver.get(HOMEPAGE)
        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("test", Keys.RETURN)
        WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.XPATH, "//div[2]/div[1]/div/div[1]/a/div[2]/h3"))
        assert driver.find_element(By.XPATH, "//h3[contains(., 'Kabeltestare')]")

    def test_choose_store(self, driver):
        driver.get(HOMEPAGE)
        driver.maximize_window()
        self.wait_and_click(driver, "//div[3]/div/button")  # menu button
        self.wait_and_click(driver, "//nav/div/div[9]/div")  # choose store
        self.wait_and_click(driver, "//li[contains(.,'Kalmar')]")  # select store
        self.wait_and_click(driver, "//div[2]/div/div[5]/button")  # accept store
        self.wait_and_click(driver, "//div[3]/div/button[1]")  # menu button

        # check chosen store
        WebDriverWait(driver, timeout=5).until(lambda d: d.find_element(By.XPATH, "//nav/div/div[9]/div[1]/div/div[2]"))
        chosen_store = driver.find_element(By.XPATH, "//nav/div/div[9]/div[1]/div/div[2]")
        assert "kalmar" in chosen_store.text.lower()


# if __name__ == "__main__":
#  pass
