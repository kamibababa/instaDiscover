import time
import logging
import json

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class InstaDiscover:

    def __init__(self):
        with open("config.json", "r") as file:
            self.config = json.load(file)
        self.chrome: webdriver = webdriver.Chrome()  # openBrowser
        self.url = 'https://www.instagram.com'

    def close_browser(self):
        time.sleep(10)
        self.chrome.close()

    def login(self):
        self.chrome.get(self.url + '/accounts/login/')
        time.sleep(3)  # loading login screen
        username = self.chrome.find_element(By.NAME, 'username')
        password = self.chrome.find_element(By.NAME, 'password')
        loginButton = self.chrome.find_element(By.XPATH, "//button[1][@type='submit']")
        username.send_keys(self.config['login']['username'])
        password.send_keys(self.config['login']['password'])
        time.sleep(1)
        loginButton.click()
        logging.info('Logged in')
        time.sleep(3)


if __name__ == '__main__':
    # try:
    logging.basicConfig(filename='process.log', encoding='utf-8', level=logging.INFO)
    insta = InstaDiscover()
    insta.login()
    insta.close_browser()
    # except Exception:
    #     logging.exception("message")
