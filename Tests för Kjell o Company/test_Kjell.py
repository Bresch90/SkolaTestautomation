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
            driver = webdriver.Chrome()
        case "firefox":
            driver = webdriver.Firefox()
        case "edge":
            driver = webdriver.Edge()
        case _:
            raise ValueError(f"Bad input from --browser variable [{browser}]. Did you misspell it?")

    yield driver
    driver.delete_all_cookies()
    driver.quit()


def wait_and_click(active_driver, path):
    WebDriverWait(active_driver, timeout=5).until(lambda d: d.find_element(By.XPATH, path))
    element = active_driver.find_element(By.XPATH, path)
    element.click()


def wait_and_get_element(active_driver, path):
    WebDriverWait(active_driver, timeout=5).until(lambda d: d.find_element(By.XPATH, path))
    return active_driver.find_element(By.XPATH, path)


class TestKjell:
    def test_open_homepage(self, driver):
        driver.get(HOMEPAGE)
        assert "kjell" in driver.title.lower()

    def test_search_bar(self, driver):
        driver.get(HOMEPAGE)
        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("test", Keys.RETURN)

        # get product from search results
        example_element = wait_and_get_element(driver, "//h3[contains(., 'Kabeltestare')]")
        assert example_element

    def test_choose_store(self, driver):
        driver.get(HOMEPAGE)
        driver.maximize_window()  # menu button has different path if screen is too small.
        wait_and_click(driver, "//div[3]/div/button")  # menu button
        wait_and_click(driver, "//nav/div/div[9]/div")  # choose store
        wait_and_click(driver, "//li[contains(.,'Kalmar')]")  # select store
        wait_and_click(driver, "//div[2]/div/div[5]/button")  # accept store
        wait_and_click(driver, "//div[3]/div/button[1]")  # menu button

        # check chosen store
        chosen_store = wait_and_get_element(driver, "//nav/div/div[9]/div[1]/div/div[2]")
        assert "kalmar" in chosen_store.text.lower()


# if __name__ == "__main__":
#  pass
