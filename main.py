import sys
import time
import logging
import json

from selenium.webdriver import Keys

from helpers import array_helper
from helpers import database_helper

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # read network


class InstaDiscover:

    def load_config(self):
        with open("config.json", "r") as file:
            self.config = json.load(file)

    def configuration_driver(self):
        desired_capabilities = DesiredCapabilities.CHROME
        desired_capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless') # hide window
        options.add_argument("--ignore-certificate-errors")
        self.driver: webdriver = webdriver.Chrome(options=options, desired_capabilities=desired_capabilities)

    def set_default_values(self):
        self.url = 'https://www.instagram.com'

    def read_network_log(self, url):
        logs = self.driver.get_log("performance")
        for log in logs:
            network_log = json.loads(log["message"])["message"]
            if "Network.response" in network_log["method"]:
                if array_helper.keys_exists(network_log, ['params', 'response', 'url']) is True:
                    if network_log['params']['response']['url'].find(url) != -1:
                        return json.loads(self.driver.execute_cdp_cmd(
                            'Network.getResponseBody', {'requestId': network_log["params"]["requestId"]}
                        )['body'])

        return None

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
        time.sleep(3)

    def discover(self):
        self.driver.get(self.url + '/explore/people/')
        time.sleep(3)  # loading discover screen
        response = self.read_network_log(self.url + '/api/v1/discover/ayml/')
        if response is not None:
            if array_helper.keys_exists(response, ['groups', 0, 'items']) is True:
                items = response['groups'][0]['items']
                for item in items:
                    if array_helper.keys_exists(item, ['user', 'username']) is True:
                        database_helper.insert(database_helper.TABLE.DISCOVER_USERS.value, {
                            'insta_id': item['user']['pk'],
                            'username': item['user']['username'],
                            'full_name': item['user']['full_name'],
                            'profile_pic_url': item['user']['profile_pic_url'],
                        })
                database_helper.commit()
                follow_buttons = self.driver.find_elements(By.XPATH, "//*[@class='_acan _acap _acas _aj1-']")
                for follow_button in follow_buttons:
                    follow_button.click()
                    time.sleep(1)
                time.sleep(2)


if __name__ == '__main__':
    # try:
    logging.basicConfig(filename='process.log', encoding='utf-8', level=logging.INFO)

    logging.info('step 1')
    insta = InstaDiscover()
    logging.info('step 2')
    insta.login()
    logging.info('step 3')
    insta.discover()

    insta.close_browser()

    # except Exception:
    #     logging.exception("message")
