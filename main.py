import time
import logging
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # read network


class InstaDiscover:

    def load_config(self):
        with open("config.json", "r") as file:
            self.config = json.load(file)
            logging.info(self.config)

    def configuration_driver(self):
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless') # hide window
        options.add_argument("--ignore-certificate-errors")
        self.driver: webdriver = webdriver.Chrome(options=options, desired_capabilities=desired_capabilities)

    def set_default_values(self):
        self.url = 'https://www.instagram.com'

    def read_network_log(self):
        logs = self.driver.get_log("performance")
        # logging.info(logs)
        for log in logs:
            logging.info(log)
            # network_log = json.loads(log["message"])["message"]
            # if ("Network.response" in network_log["method"])

    def __init__(self):
        self.driver: webdriver.Chrome | None = None
        self.config = None
        self.url = None

        self.configuration_driver()
        self.load_config()
        self.set_default_values()

    def close_browser(self):
        time.sleep(10)
        self.driver.close()

    def login(self):
        self.driver.get(self.url + '/accounts/login/')
        time.sleep(3)  # loading login screen
        username = self.driver.find_element(By.NAME, 'username')
        password = self.driver.find_element(By.NAME, 'password')
        loginButton = self.driver.find_element(By.XPATH, "//button[1][@type='submit']")
        username.send_keys(self.config['login']['username'])
        password.send_keys(self.config['login']['password'])
        time.sleep(1)
        loginButton.click()
        logging.info('Logged in')
        self.read_network_log()
        time.sleep(3)

    def discover(self):
        self.driver.get(self.url + '/explore/people/')


if __name__ == '__main__':
    # try:
    logging.basicConfig(filename='process.log', encoding='utf-8', level=logging.INFO)
    insta = InstaDiscover()
    insta.login()
    insta.discover()
    insta.close_browser()
    # except Exception:
    #     logging.exception("message")
