from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
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
            from selenium.webdriver.chrome.options import Options
            options = Options()
            options.add_argument('--headless')
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=options)
        case "firefox":
            from selenium.webdriver.firefox.options import Options
            options = Options()
            options.add_argument('--headless')
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Firefox(options=options)
        case "edge":
            from selenium.webdriver.edge.options import Options
            options = Options()
            options.add_argument('--headless')
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Edge(options=options)
        case _:
            raise ValueError(f"Bad input from --browser variable [{browser}]. Did you misspell it?")

    yield driver
    driver.delete_all_cookies()
    driver.quit()


def wait_and_click(active_driver, path):
    WebDriverWait(active_driver, timeout=5).until(ec.element_to_be_clickable((By.XPATH, path))).click()


def wait_and_get_element(active_driver, path):
    return WebDriverWait(active_driver, timeout=5).until(ec.element_to_be_clickable((By.XPATH, path)))


def add_to_cart(active_driver):
    # add to cart
    wait_and_click(active_driver, "//*[@id='addToCart']")
    # close overlay window. Using javascript as the element animates and something captures the click
    active_driver.execute_script("arguments[0].click();",
                                 active_driver.find_element(By.XPATH, "//button[@data-test-id='recs-close-btn']"))


class TestKjell:
    def test_open_homepage(self, driver):
        driver.get(HOMEPAGE)
        assert "kjell" in driver.title.lower()

    def test_search_bar(self, driver):
        driver.get(HOMEPAGE)
        # accept cookies as it obscures some options
        wait_and_click(driver, "//div[3]/button[2]")
        driver.maximize_window()  # menu button has different path if screen is too small.
        search_bar = wait_and_get_element(driver, '//form/div[1]/input')
        search_bar.send_keys("test", Keys.RETURN)

        # get product from search results
        example_element = wait_and_get_element(driver, "//h3[contains(., 'Kabeltestare')]")
        assert example_element

    def test_choose_store(self, driver):
        driver.get(HOMEPAGE)
        driver.maximize_window()  # menu button has different path if screen is too small.
        wait_and_click(driver, "//button[@data-test-id='main-menu-button']")  # menu button
        wait_and_click(driver, "//div[@data-test-id='my-store-button']")  # choose store
        wait_and_click(driver, "//li[contains(.,'Kalmar')]")  # select store
        wait_and_click(driver, "//button[@data-test-id='choose-store-button']")  # accept store
        wait_and_click(driver, "//button[@data-test-id='main-menu-button']")  # menu button

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

        # wait for element on left side to load
        wait_and_get_element(driver, "//div[2]/div/div[1]/div[1]/div[2]")
        products_list = [e.text for e in driver.find_elements(By.XPATH, "//h3")]
        assert "test" in products_list[0].lower()

    def test_add_to_cart(self, driver):
        item_names_list = []
        prices_dict = {}
        product_positions = [2, 2, 2, 2, 2, 4, 7, 22, 15, 12, 14, 13, 11]

        driver.get(HOMEPAGE)
        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("test", Keys.RETURN)
        # wait for element on left side to load
        wait_and_get_element(driver, "//div[2]/div/div[1]/div[1]/div[2]")
        # collect data on the products and add to cart
        for pos in product_positions:
            # scrolls to element as some are in the dom but cant be clicked.
            driver.execute_script("arguments[0].scrollIntoView();",
                                  driver.find_element(By.XPATH, f"//div[1]/div/div[{pos}]/a"))
            wait_and_click(driver, f"//div[1]/div/div[{pos}]/a")
            print(f"\ngoing on {pos=}")
            name = wait_and_get_element(driver, f"//section[1]/div[1]/h1").text
            if name not in item_names_list:
                item_names_list.append(name)
            price = float(wait_and_get_element(driver, f"//section[1]/div[2]/div[2]/span/span")
                          .text.replace(':-', '').replace(' ', ''))  # some contain ":-" and spaces

            # correcting cents(öre) being added as full price. If it has a /sup, its being corrected.
            if driver.find_elements(By.XPATH, f"//section[1]/div[2]/div[2]/span/span/sup"):
                price /= 100
            if name in prices_dict:
                prices_dict[name] = prices_dict[name] + price
            else:
                prices_dict.update({name: price})

            add_to_cart(driver)
            driver.back()

        # open cart
        wait_and_click(driver, "//button[@data-test-id='cart-button']")
        # get total from cart and format string
        total_cart_site = wait_and_get_element(driver, "//div[2]/div/span/span").text.replace(' ', '').replace(':', '')
        if '-' in total_cart_site:
            total_cart_site = float(total_cart_site.replace('-', ''))
        else:
            total_cart_site = float(total_cart_site)/100  # correct if cents

        items_in_cart = [e.text for e in driver.find_elements(By.XPATH, "//li/div[1]/div[1]/div/a")]
        for item in item_names_list:
            assert item in items_in_cart

        # print(f"\n{prices_dict} {total_cart_site} {sum(prices_dict.values())}")
        assert f"{sum(prices_dict.values()):.1f}" == f"{total_cart_site:.1f}"  # string to format floating point error

