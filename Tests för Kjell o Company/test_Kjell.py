from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
import logging
import pytest
from time import sleep

HOMEPAGE = "https://www.kjell.com/se/"
BROWSER = ''
HEADLESS = ''
logging.basicConfig(level=logging.WARNING)
DEFAULT_MAX_FAILS = 5
MAX_TIMEOUT = 30


@pytest.fixture(autouse=True, scope='function')
def driver(request):
    global BROWSER, HEADLESS
    # needed a global variable since it can only be fetched once it seems.
    BROWSER = request.config.getoption('--browser').lower()
    HEADLESS = request.config.getoption('--headless').lower()

    # BROWSER = 'edge'
    match BROWSER:
        case "chrome":
            from selenium.webdriver.chrome.options import Options
            options = Options()
            if HEADLESS == 'true':
                options.add_argument('--headless')
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Chrome(options=options)
        case "firefox":
            from selenium.webdriver.firefox.options import Options
            options = Options()
            if HEADLESS == 'true':
                options.add_argument('--headless')
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            driver = webdriver.Firefox(options=options)
        case "edge":
            from selenium.webdriver.edge.options import Options
            options = Options()
            if HEADLESS == 'true':
                options.add_argument('--headless')
            options.add_argument("--window-size=1920,1080")
            driver = webdriver.Edge(options=options)
        case _:
            raise ValueError(f"Bad input from --browser variable [{BROWSER}]. Did you misspell it?")
    driver.get(HOMEPAGE)
    # accept cookies as it obscures some elements
    wait_and_click(driver, "//div[3]/button[2]")
    yield driver
    driver.delete_all_cookies()
    driver.quit()


def wait_and_click(active_driver, path, center_scroll=True, max_fails=DEFAULT_MAX_FAILS):
    tries = 0
    while True:
        try:
            # wait for element to be available if needed.
            element = WebDriverWait(active_driver, timeout=MAX_TIMEOUT).until(
                ec.element_to_be_clickable((By.XPATH, path)))
            # move_to_element action doesn't scroll on firefox, had to use javascript instead.
            active_driver.execute_script("arguments[0].scrollIntoView(true);", element)
            if center_scroll:
                active_driver.execute_script("window.scrollBy(0, -650);")  # center on screen after scroll.
            # ActionChains(active_driver).move_to_element(element).click().perform()  # works without firefox
            WebDriverWait(active_driver, timeout=MAX_TIMEOUT).until(
                ec.element_to_be_clickable((By.XPATH, path))).click()
            return
        except StaleElementReferenceException as e:
            logging.warning(f"Element {path=} was stale! Trying again")
            tries += 1
            if tries > max_fails:
                raise StaleElementReferenceException("Too many stale elements!")
            sleep(1)
        except ElementClickInterceptedException as e:
            logging.warning(f"Click on element {path=} was intercepted! Trying again")
            tries += 1
            if tries > max_fails:
                raise ElementClickInterceptedException("Too many click intercepts!")
            sleep(1)
        except TimeoutException as e:
            logging.warning(f"Timeout on element {path=}! Trying again")
            tries += 1
            if tries > max_fails:
                raise TimeoutException("Too many timeouts!")
            sleep(1)


def wait_and_get_element(active_driver, path, center_scroll=True, max_fails=DEFAULT_MAX_FAILS):
    tries = 0
    while True:
        try:
            # wait for element to be available if needed.
            element = WebDriverWait(active_driver, timeout=MAX_TIMEOUT).until(
                ec.element_to_be_clickable((By.XPATH, path)))
            # move_to_element action doesn't scroll on firefox, had to use javascript instead.
            active_driver.execute_script("arguments[0].scrollIntoView(true);", element)
            if center_scroll:
                active_driver.execute_script("window.scrollBy(0, -650);")  # center on screen after scroll.
            # need to fetch element again since the page destroys some elements when scrolling.
            # this fixed the assertion error with getting name being different on some browsers?
            return WebDriverWait(active_driver, timeout=MAX_TIMEOUT).until(
                ec.element_to_be_clickable((By.XPATH, path)))
        except StaleElementReferenceException as e:
            logging.warning(f"Element {path=} was stale! Trying again")
            tries += 1
            if tries > max_fails:
                raise StaleElementReferenceException("Too many stale elements!")
            sleep(1)
        except ElementClickInterceptedException as e:
            logging.warning(f"Click on element {path=} was intercepted! Trying again")
            tries += 1
            if tries > max_fails:
                raise ElementClickInterceptedException("Too many click intercepts!")
            sleep(1)
        except TimeoutException as e:
            logging.warning(f"Timeout on element {path=}! Trying again")
            tries += 1
            if tries > max_fails:
                raise TimeoutException("Too many timeouts!")
            sleep(1)


class TestKjell:
    def test_open_homepage(self, driver):
        assert "kjell" in driver.title.lower()

    def test_search_bar(self, driver):
        search_bar = wait_and_get_element(driver, '//form/div[1]/input')
        search_bar.send_keys("test", Keys.RETURN)

        # get product from search results
        example_element = wait_and_get_element(driver, "//h3[contains(., 'Kabeltestare')]")
        assert example_element

    def test_choose_store(self, driver):
        wait_and_click(driver, "//button[@data-test-id='main-menu-button']")  # menu button
        wait_and_click(driver, "//div[@data-test-id='my-store-button']", center_scroll=False)  # choose store
        wait_and_click(driver, "//li[contains(.,'Kalmar')]")  # select store
        wait_and_click(driver, "//button[@data-test-id='choose-store-button']", center_scroll=False)  # accept store
        wait_and_click(driver, "//button[@data-test-id='main-menu-button']")  # menu button
        # check chosen store
        chosen_store = wait_and_get_element(driver, "//nav/div/div[9]/div[1]/div/div[2]", center_scroll=False)
        assert "kalmar" in chosen_store.text.lower()

    @pytest.mark.skip(reason="test_search_exact: Not implemented on site. "
                             "Does something with quotation but doesnt search for exact.")
    def test_search_exact(self, driver):
        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("\"test\"", Keys.RETURN)
        wait_and_get_element(driver, "//div[2]/div/div[1]/div[1]/div[2]")  # wait for element on left side to load
        products_list = [e.text for e in driver.find_elements(By.XPATH, "//h3")]
        assert "test" in products_list[0].lower()

    def test_find_item_out_of_stock(self, driver):
        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("test", Keys.RETURN)
        wait_and_get_element(driver, "//div[2]/div/div[1]/div[1]/div[2]")  # wait for element on left side to load
        # gets first item that is out of stock and clicks it
        wait_and_click(driver, "//*[@id='outofstock_a']/../../../../../../a")
        # checks if the button "Bevaka" is there instead of add to cart.
        assert WebDriverWait(driver, timeout=MAX_TIMEOUT).until(
            lambda d: d.find_elements(By.XPATH, "//button[contains(., 'Bevaka')]")
        )

    def test_add_to_cart(self, driver):
        products_dict = {}
        product_positions = [2, 3, 2, 5, 6, 4, 7, 8, 22, 22, 15, 12, 14, 13, 11]
        # product_positions = [1, 2, 1, 19, 30, 25, 1, 3, 18, 18] # for testing different items

        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("test", Keys.RETURN)
        wait_and_get_element(driver, "//div[2]/div/div[1]/div[1]/div[2]")  # wait for element on left side to load
        # collect data on the products and add to cart
        for pos in product_positions:
            # click on product
            wait_and_click(driver, f"//div[1]/div/div[{pos}]/a")  # max_fails because edge in jenkins
            logging.info(f"going on {pos=}")
            # wait for product page to load a slow element
            wait_and_get_element(driver, "//span[contains(., 'ställ en fråga')]", center_scroll=False)
            name = wait_and_get_element(driver, f"//div[1]/h1").text
            # wait for addToCart or "Bevaka" button
            WebDriverWait(driver, timeout=MAX_TIMEOUT).until(
                lambda d:
                d.find_elements(By.XPATH, "//*[@id='addToCart']")
                or d.find_elements(By.XPATH, "//button[contains(., 'Bevaka')]")
            )
            # check if item is out of stock
            if driver.find_elements(By.XPATH, "//button[contains(., 'Bevaka')]"):
                logging.info(f"\n{name} {pos=} is not available for purchase, skipping it")
                driver.back()
                continue

            price = float(wait_and_get_element(driver,
                                               f'//div/span/span')
                          .text.replace(':-', '').replace(' ', ''))  # some contain ":-" and spaces
            # looking for both sup on mobile layout and normal
            if driver.find_elements(By.XPATH, f"//section[1]/div[2]/div[2]/span/span/sup") or \
                    driver.find_elements(By.XPATH, f"//div[3]/span/span/sup") or \
                    driver.find_elements(By.XPATH,
                                         f"/html/body/div[1]/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/span/span/sup"):
                # last one is because some elements behave wierd with path to sup...for example:
                # https://www.kjell.com/se/produkter/el-verktyg/matinstrument/matsladdar-prober-kontakter/matsladdar/matsladdar-30-v-3-pack-p37842
                price /= 100
                logging.info(f"Found sup! for {name}")
            else:
                logging.info(f"Didn't find sup for {name}")

            if name in products_dict:
                products_dict[name] = products_dict[name] + price
            else:
                products_dict.update({name: price})
            logging.info(f"added {name=} with {price=}")

            wait_and_click(driver, "//*[@id='addToCart']")  # add item to cart
            wait_and_get_element(driver, "//span[contains(., 'Tillagd i din varukorg')]")
            logging.info(f"cart should now be {products_dict.keys()=}")
            driver.back()

        # open cart
        wait_and_click(driver, "//button[@data-test-id='cart-button']")
        # element is on the bottom of page so no scroll back
        total_cart_site = wait_and_get_element(driver, "//div[text()='Totalt ']/span/span", center_scroll=False)\
            .text.replace(' ', '').replace(':', '')  # get total from cart and format string

        if '-' in total_cart_site:
            total_cart_site = float(total_cart_site.replace('-', ''))
        else:
            total_cart_site = float(total_cart_site)/100  # correct if there are cents
        wait_and_get_element(driver, "//div[2]/div/ul/li/div[1]/div[1]/div/a")  # make sure elements are in focus
        items_in_cart = [e.text for e in driver.find_elements(By.XPATH, "//div[2]/div/ul/li/div[1]/div[1]/div/a")]
        logging.info(f"{items_in_cart=}")
        logging.info(f"{products_dict.keys()=}")
        logging.info(f"{products_dict}")

        # checking each item in list if they match what is in the cart
        for item in products_dict.keys():
            assert item in items_in_cart
        assert f"{sum(products_dict.values()):.1f}" == f"{total_cart_site:.1f}"  # string to format floating point error
