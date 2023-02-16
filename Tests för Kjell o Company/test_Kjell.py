from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pytest
from time import sleep

HOMEPAGE = "https://www.kjell.com/se/"
browser = 'chrome'


@pytest.fixture(autouse=True, scope='class')
def driver(request):
    global browser
    # needed a global variable since it can only be fetched once it seems.
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
    WebDriverWait(active_driver, timeout=5).until(EC.element_to_be_clickable((By.XPATH, path))).click()


def wait_and_get_element(active_driver, path):
    WebDriverWait(active_driver, timeout=5).until(EC.element_to_be_clickable((By.XPATH, path)))
    return active_driver.find_element(By.XPATH, path)


def add_to_cart(active_driver):
    # add to cart
    wait_and_click(active_driver, "//*[@id='addToCart']")
    # close overlay window
    sleep(0.5)
    wait_and_click(active_driver, "//div[4]/div[2]/div[2]/div/div/div[1]/button")


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

    @pytest.mark.skip(reason="test_search_exact: Not implemented on site. "
                             "Does something with quotation but doesnt search for exact.")
    def test_search_exact(self, driver):
        driver.get(HOMEPAGE)
        driver.maximize_window()  # menu button has different path if screen is too small.
        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("\"test\"", Keys.RETURN)

        # get product from search results, needs wait?
        sleep(1)
        wait_and_get_element(driver, "//h3")
        # "//div[5]/a/div/h3"
        products_list = [e.text for e in driver.find_elements(By.XPATH, "//h3")]
        assert "test" in products_list[0].lower()

# not done yet..
    def test_add_to_cart(self, driver):
        item_names_list = []
        prices_dict = {}
        product_positions = [2, 4, 7]
        driver.get(HOMEPAGE)
        driver.maximize_window()  # menu button has different path if screen is too small.
        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("test", Keys.RETURN)
        # get product from search results, needs wait?
        sleep(1)
        # collect data on the 2nd, 4th and 7th products
        for pos in product_positions:
            # name
            item_names_list.append(wait_and_get_element(driver, f"//div[1]/div/div[{pos}]/a/div[2]/h3").text)
            # price
            price = float(wait_and_get_element(driver, f"//div[1]/div/div[{pos}]/a/div[2]/span/span")
                          .text.replace(':-', '').replace(' ', ''))

            if driver.find_elements(By.XPATH, f"//div[1]/div/div[{pos}]/a/div[2]/span/span/sup"):
                price /= 100
            prices_dict.update({item_names_list[-1]: price})
            driver.execute_script("arguments[0].scrollIntoView();",
                                  driver.find_element(By.XPATH, f"//div[1]/div/div[{pos}]/a"))
            wait_and_click(driver, f"//div[1]/div/div[{pos}]/a")
            add_to_cart(driver)
            driver.back()

        sleep(2)


