import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
import logging
import pytest
from time import sleep

HOMEPAGE = "https://www.kjell.com/se/"
BROWSER = ''
HEADLESS = ''
logging.basicConfig(level=logging.INFO)


@pytest.fixture(autouse=True, scope='function')
def driver(request):
    global BROWSER, HEADLESS
    # needed a global variable since it can only be fetched once it seems.
    # BROWSER = request.config.getoption('--browser').lower()
    HEADLESS = request.config.getoption('--headless').lower()

    BROWSER = 'edge'
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


def wait_and_click(active_driver, path, center_scroll=True, max_fails=1):
    stale_element = True
    tries = 0
    while stale_element:
        try:
            # wait for element to be available if needed.
            element = WebDriverWait(active_driver, timeout=30).until(ec.element_to_be_clickable((By.XPATH, path)))
            # move_to_element action doesn't scroll on firefox, had to use javascript instead.
            active_driver.execute_script("arguments[0].scrollIntoView(true);", element)
            if center_scroll:
                active_driver.execute_script("window.scrollBy(0, -500);")  # center on screen after scroll.
            # ActionChains(active_driver).move_to_element(element).click().perform()  # works without firefox
            WebDriverWait(active_driver, timeout=30).until(ec.element_to_be_clickable((By.XPATH, path))).click()
            stale_element = False
        except StaleElementReferenceException as e:
            logging.info("Element was stale! Trying again")
            tries += 1
        except ElementClickInterceptedException as e:
            logging.info("Click was intercepted! Trying again")
            tries += 1
        if tries > max_fails:
            raise selenium.common.exceptions.StaleElementReferenceException("Too many stale elements tries")


def wait_and_get_element(active_driver, path, center_scroll=True):
    # wait for element to be available if needed.
    element = WebDriverWait(active_driver, timeout=30).until(ec.element_to_be_clickable((By.XPATH, path)))
    # move_to_element action doesn't scroll on firefox, had to use javascript instead.
    active_driver.execute_script("arguments[0].scrollIntoView(true);", element)
    if center_scroll:
        active_driver.execute_script("window.scrollBy(0, -500);")  # center on screen after scroll.
    # need to fetch element again since the page destroys some elements when scrolling.
    # this fixed the assertion error with getting name beeing different.
    return WebDriverWait(active_driver, timeout=30).until(ec.element_to_be_clickable((By.XPATH, path)))


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
        wait_and_click(driver, "//div[@data-test-id='my-store-button']")  # choose store
        wait_and_click(driver, "//li[contains(.,'Kalmar')]")  # select store
        wait_and_click(driver, "//button[@data-test-id='choose-store-button']")  # accept store
        wait_and_click(driver, "//button[@data-test-id='main-menu-button']")  # menu button
        # check chosen store
###### check this again
        sleep(5)
        chosen_store = wait_and_get_element(driver, "//nav/div/div[9]/div[1]/div/div[2]")
        # "/html/body/div[1]/div[1]/div/div[6]/div[2]/div/div/div/div[2]/nav/div/div[9]/div[1]/div/div[2]" # stor skärm
        # "/html/body/div[1]/div[1]/div/div[6]/div[2]/div/div/div/div[2]/nav/div/div[9]/div[1]/div/div[2]"
        assert "kalmar" in chosen_store.text.lower()

    @pytest.mark.skip(reason="test_search_exact: Not implemented on site. "
                             "Does something with quotation but doesnt search for exact.")
    def test_search_exact(self, driver):
        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("\"test\"", Keys.RETURN)

        # wait for element on left side to load
        wait_and_get_element(driver, "//div[2]/div/div[1]/div[1]/div[2]")
        products_list = [e.text for e in driver.find_elements(By.XPATH, "//h3")]
        assert "test" in products_list[0].lower()

    def test_add_to_cart(self, driver):
        item_names_list = []
        prices_dict = {}
        # product_positions = [2, 2, 2, 2, 6, 4, 7, 22, 15, 12, 14, 13, 11]
        product_positions = [2, 6, 7, 22]

        search_bar = driver.find_element(By.XPATH, '//form/div[1]/input')
        search_bar.send_keys("test", Keys.RETURN)
        # wait for element on left side to load
        wait_and_get_element(driver, "//div[2]/div/div[1]/div[1]/div[2]")
        # collect data on the products and add to cart
        for pos in product_positions:
            wait_and_click(driver, f"//div[1]/div/div[{pos}]/a", max_fails=10)  # click on product
            logging.info(f"\ngoing on {pos=}")
            name = wait_and_get_element(driver, f"//div[1]/h1").text
            # wait for addToCart or "Bevaka" button
            WebDriverWait(driver, timeout=30).until(lambda d:
                                                    d.find_elements(By.XPATH, "//*[@id='addToCart']")
                                                    or d.find_elements(By.XPATH, "//button[contains(., 'Bevaka')]")
                                                    )
            # check if item is out of stock
            if driver.find_elements(By.XPATH, "//button[contains(., 'Bevaka')]"):
                logging.info(f"\n{name} {pos=} is not available for purchase, skipping it")
                driver.back()
                continue

            if name not in item_names_list:
                item_names_list.append(name)
                logging.info(f"added {name} to item_names_list")
            price = float(wait_and_get_element(driver,
                                               f'//div/span/span')
                          .text.replace(':-', '').replace(' ', ''))  # some contain ":-" and spaces
            # looking for both sup on mobile layout and normal
            if driver.find_elements(By.XPATH, f"//section[1]/div[2]/div[2]/span/span/sup") or \
                    driver.find_elements(By.XPATH, f"//div[3]/span/span/sup") or \
                    driver.find_elements(By.XPATH, f"/html/body/div[1]/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/span/span/sup"):
                # last one is because some elements behave wierd with path to sup...for example:
                # https://www.kjell.com/se/produkter/el-verktyg/matinstrument/matsladdar-prober-kontakter/matsladdar/matsladdar-30-v-3-pack-p37842
                "/html/body/div[1]/div[1]/div/div[4]/section[1]/div[2]/div[2]/span/span/sup"
                "/html/body/div[1]/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/span/span/sup"

                "/html/body/div[1]/div[1]/div/div[4]/section[1]/div[2]/div[2]/span/span/sup" # stor röv
                "/html/body/div[1]/div[1]/div/div[4]/div/div[1]/div[1]/div[2]/span/span/sup" # liten röv

                "/html/body/div/div[1]/div/div[4]/section[1]/div[2]/div[2]/span/span/sup" # stor, semi normal
                "/html/body/div/div[1]/div/div[4]/div/div[1]/div[1]/div[3]/span/span/sup" # liten semi normal

                "/html/body/div/div[1]/div/div[4]/section[1]/div[2]/div[2]/span/span/sup" # stor normal
                "/html/body/div/div[1]/div/div[4]/div/div[1]/div[1]/div[3]/span/span/sup" # liten normal

                price /= 100
                logging.info(f"Found sup! for {name}")
            else:
                logging.info(f"Didn't find sup for {name}")

            if name in prices_dict:
                prices_dict[name] = prices_dict[name] + price
            else:
                prices_dict.update({name: price})

            wait_and_click(driver, "//*[@id='addToCart']")  # add item to cart
            logging.info(f"cart should now be {item_names_list=}")
            driver.back()

        # open cart
        wait_and_click(driver, "//button[@data-test-id='cart-button']")
        total_cart_site = wait_and_get_element(driver, "//div[2]/div[2]/div/span/span", center_scroll=False)\
            .text.replace(' ', '').replace(':', '')  # get total from cart and format string

        "/html/body/div[1]/div[1]/div/div[6]/div[2]/div/div/div[2]/div/div[2]/div[2]/div/span/span"
        "/html/body/div[1]/div[1]/div/div[6]/div[2]/div/div/div[2]/div/div[2]/div[2]/div/span/span"

        if '-' in total_cart_site:
            total_cart_site = float(total_cart_site.replace('-', ''))
        else:
            total_cart_site = float(total_cart_site)/100  # correct if there are cents
        wait_and_get_element(driver, "//div[2]/div/ul/li/div[1]/div[1]/div/a")  # make sure elements are in focus
        items_in_cart = [e.text for e in driver.find_elements(By.XPATH, "//div[2]/div/ul/li/div[1]/div[1]/div/a")]
        logging.info(f"{items_in_cart=}")
        logging.info(f"{item_names_list=}")
        logging.info(f"{prices_dict}")
        for item in item_names_list:
            item_was_found = False
            for item_in_cart in items_in_cart:
                if item in item_in_cart:
                    item_was_found = True
                    break
            assert item_was_found

        assert f"{sum(prices_dict.values()):.1f}" == f"{total_cart_site:.1f}"  # string to format floating point error

