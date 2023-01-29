import undetected_chromedriver.v2 as ChromeDriver
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep

options = webdriver.ChromeOptions()
options.add_argument("--incognito")

driver = ChromeDriver.Chrome(options=options)

test_url = "https://wall.alphacoders.com/"

driver.get(test_url)

print(driver.title)
sleep(5)

search_bar = driver.find_element(by=By.CSS_SELECTOR, value=".input-lg")
search_button = driver.find_element(by=By.CSS_SELECTOR, value=".btn-lg")
search_bar.send_keys("Testing stuffs")
sleep(5)
search_button.click()
sleep(20)
print(driver.title)

driver.quit()
