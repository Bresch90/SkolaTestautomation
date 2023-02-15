import undetected_chromedriver.v2 as chrome_driver
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep

options = ChromeOptions()
options.add_argument("--incognito")
driver = chrome_driver.Chrome(options=options)


# waiting with functions. Fleshing out the script to find where functions are needed or can be reused.
def open_page(url: str):
    driver.get(url)


def search_with_bar(search_str: str):
    search_bar = driver.find_element(by=By.NAME, value="search")
    search_bar.send_keys(search_str, Keys.RETURN)


def find_element_with_css(css_str: str):
    pass


if __name__ == "__main__":
    open_page("https://wall.alphacoders.com/")
    search_with_bar("For academic purposes only")
    sleep(5)
    driver.quit()
