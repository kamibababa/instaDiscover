import sys
import time
import logging
import json

from selenium.common import NoSuchElementException
from selenium.webdriver import Keys

from helpers import array_helper
from helpers import database_helper

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # read network
from datetime import datetime, timedelta


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

    def read_network_logs(self, url):
        data = []
        logs = self.driver.get_log("performance")
        for log in logs:
            network_log = json.loads(log["message"])["message"]
            if "Network.response" in network_log["method"]:
                if array_helper.keys_exists(network_log, ['params', 'response', 'url']) is True:
                    if network_log['params']['response']['url'].find(url) != -1:
                        data.append(json.loads(self.driver.execute_cdp_cmd(
                            'Network.getResponseBody', {'requestId': network_log["params"]["requestId"]}
                        )['body']))

        return data

    def __init__(self):
        self.driver: webdriver.Chrome | None = None
        self.config = None
        self.url = None

        self.configuration_driver()
        self.load_config()
        self.set_default_values()

        self.account_name = self.config['login']['username']

    def close_browser(self):
        print('closing browser')
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
        time.sleep(6)

    def discover(self):
        try:
            self.driver.get(self.url + '/explore/people/')
            time.sleep(3)  # loading discover screen

            response = self.read_network_log(self.url + '/api/v1/discover/ayml/')
            if response is not None:
                if array_helper.keys_exists(response, ['groups', 0, 'items']) is True:
                    items = response['groups'][0]['items']
                    for item in items:
                        if array_helper.keys_exists(item, ['user', 'username']) is True:
                            # daha önceden bu username veritabanına kayıt olmuş mu ?
                            if database_helper.find('discover_users',
                                                    "username='" + item['user']['username'] + "'",
                                                    'id,username') is None:

                                if int(item['is_verified']) is False:
                                    database_helper.insert('discover_users', {
                                        'account_name': self.account_name,
                                        'insta_id': item['user']['pk'],
                                        'username': item['user']['username'],
                                        'full_name': item['user']['full_name'],
                                        'is_verified': int(item['is_verified']),
                                        'profile_pic_url': item['user']['profile_pic_url'],
                                        'expires_at': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
                                    })
                    database_helper.commit()
                    self.follows_press()
                    time.sleep(2)
        except Exception as e:
            logging.error(str(e))
            print('Error: ' + str(e))

    def check_up_users(self):

        discover_users = database_helper.find_all(
            'discover_users',
            'id, username, expires_at, last_follow_request_at, follow_request_count'
        )

        for discover_user in discover_users:
            username = discover_user['username']
            self.driver.get(self.url + '/' + username + '/')
            time.sleep(10)  # loading profile
            try:
                response = self.read_network_log(self.url + '/api/v1/users/web_profile_info/?username=' + username)
                if response is not None:
                    if array_helper.keys_exists(response, ['data', 'user']) is True:
                        user = response['data']['user']
                        """
                        requested_by_viewer: true //takip istegi yollanmis
                        followed_by_viewer: false //takip istegimi kabul edilmis
                        follows_viewer: false // takip istegini kabul etmisim
                        """
                        database_helper.update(  # ilgili kisiyle alakali son durum guncellemesi
                            'discover_users',
                            'id=' + str(discover_user['id']), {
                                'requested_by_viewer': int(user['requested_by_viewer']),
                                'followed_by_viewer': int(user['followed_by_viewer']),
                                'follows_viewer': int(user['follows_viewer']),
                                'is_verified': int(user['is_verified'])
                            }
                        )

                        if user['follows_viewer']:  # takip isteğini kabul etmişim o beni takip ediyor
                            self.extend_expires(discover_user)
                            print(discover_user['username'] + ' kişi takipte kaldığı için kontrol süresi uzatıldı.')
                            time.sleep(1)
                        elif user['requested_by_viewer']:  # takip isteği atılmış ve bekliyor
                            if (datetime.now() - discover_user['last_follow_request_at']).days > 15:
                                # gönderilen istek iptal ediliyor.
                                self.unfollow_press()
                                database_helper.delete('discover_users',
                                                       'id=' + str(discover_user['id']))
                                print(discover_user['username'] +
                                      ' takip isteği 15 günü aşmış user silinecek ve istek iptal edilecek!')
                            else:
                                print(
                                    discover_user['username'] + ' takip isteği gönderilmiş beklemede 15 günü aşmamış.')
                            time.sleep(1)
                        elif user['followed_by_viewer'] is False:  # takip isteği atmışım ancak reddetmiş
                            print(discover_user['username'] + ' atılan takip isteğini iptal etmiş.')
                            self.follower_evaluation(discover_user)
                            time.sleep(1)
                        else:  # followed_by_viewer is True # Takip isteği atmışım ve istek bekliyor
                            # geri takip suresi asilmis mi veya kontrol süresi aşılmış mı ?
                            if datetime.now() > discover_user['expires_at']:
                                self.unfollow_press()  # takip den cıkılıyor
                                follower_evaluation_status = self.follower_evaluation(discover_user)  # degerlendirme
                                if follower_evaluation_status is True:
                                    print(discover_user['username']
                                          + ' geri takip süresi aşılmış ve değerlendirme iptal oldu!')
                                else:
                                    self.extend_expires(discover_user)
                                    print(discover_user['username'] + ' değerlendirme süresi verildi')
                                time.sleep(1)
                else:
                    print(discover_user['username'] + ' ERISIM SAGLANAMADI')
            except Exception as e:
                logging.error(str(e))
                print('Error: ' + str(e))

    def unfollow_press(self):
        try:
            self.driver.find_element(By.XPATH, "//*[@class='_acan _acap _acat _aj1-']").click()  # unfollow button
            time.sleep(1)
            self.driver.find_element(By.XPATH, "//*[@class='_abm4'][5]").click()  # popup approved button
            time.sleep(2)
        except NoSuchElementException:
            print('Unfollow butonu bulunamadı')

    def follows_press(self):
        follow_buttons = self.driver.find_elements(By.XPATH, "//*[@class='_acan _acap _acas _aj1-']")
        for follow_button in follow_buttons:
            follow_button.click()
            time.sleep(1)
        time.sleep(2)

    def follower_evaluation(self, discover_user):
        if discover_user['follow_request_count'] > 4:
            database_helper.delete('discover_users',
                                   'id=' + str(discover_user['id']))
            print(discover_user['username'] + ' 4 kez takip isteği kabul edilmemiş user silindi!')
            return True
        else:
            # Takip et butonuna basılıyor
            self.follows_press()
            database_helper.update(
                'discover_users', 'id=' + str(discover_user['id']), {
                    'follow_request_count': discover_user['follow_request_count'] + 1,
                    'last_follow_request_at': datetime.now()
                }
            )
            print(discover_user['username'] + ' ait '
                  + str(discover_user['follow_request_count'] + 1) + ' kez takip isteği gönderildi')
            time.sleep(1)
            return False

    def extend_expires(self, discover_user):
        database_helper.update(
            'discover_users',
            'id=' + str(discover_user['id']), {
                'expires_at': (discover_user['expires_at'] + timedelta(days=5))
            }
        )

    def get_profile_info(self, profile_name, url=''):
        self.driver.get(self.url + '/' + profile_name + '/' + url)
        time.sleep(2)  # loading profile
        response = self.read_network_log(self.url + '/api/v1/users/web_profile_info/?username=' + profile_name)
        if response is not None:
            if array_helper.keys_exists(response, ['data', 'user']) is True:
                return response['data']['user']
        return None

    def sync_followers(self):
        profile = self.get_profile_info(self.account_name, 'followers')
        if profile is not None:
            # followerButtom = self.driver.find_elements(By.XPATH, "//*[@class='_aacl _aacp _aacu _aacx _aad6 _aade']")[1]
            # followerButtom.click()
            time.sleep(2)  # loading followers
            tempScrollHeight = self.driver.execute_script(
                "return document.getElementsByClassName('_aano')[0].scrollHeight")
            while True:
                # scroll down
                self.driver.execute_script(
                    "document.getElementsByClassName('_aano')[0].scrollTop = "
                    "document.getElementsByClassName('_aano')[0].scrollHeight")
                time.sleep(3)  # scrolldown ediltikden sonra yuklemeyi bekliyoruz.
                scrollHeight = self.driver.execute_script(
                    "return document.getElementsByClassName('_aano')[0].scrollHeight")
                if tempScrollHeight == scrollHeight:  # ayni scrollheight sahip ise daha sona gidermiyor demektir.
                    print('ended scroll down')
                    break
                else:
                    tempScrollHeight = scrollHeight

            time.sleep(2)  # loading network
            responses = self.read_network_logs(
                self.url + '/api/v1/friendships/' + str(profile['id']) + '/followers/?count=12')
            usernames = ''
            for response in responses:
                for user in response['users']:
                    usernames += "'" + user['username'] + "',"
                    find_result = database_helper.find(
                        'followers', "account_name='" + self.account_name + "' AND username='" + user['username'] + "'",
                        'id,username')
                    if find_result is None:
                        database_helper.insert('followers', {
                            'account_name': self.account_name,
                            'insta_id': user['pk'],
                            'username': user['username'],
                            'full_name': user['full_name'],
                            'is_verified': user['is_verified'],
                            'profile_pic_url': user['profile_pic_url']
                        }, True)
                    else:
                        database_helper.update('followers', 'id=' + str(find_result['id']), {
                            'account_name': self.account_name,
                            'insta_id': user['pk'],
                            'username': user['username'],
                            'full_name': user['full_name'],
                            'is_verified': user['is_verified'],
                            'profile_pic_url': user['profile_pic_url']
                        })
            if usernames != '':
                usernames = usernames.rstrip(',')
                database_helper.delete(
                    'followers', "account_name='" + self.account_name + "' AND username NOT IN(" + usernames + ")")

            print('synchronized followers')
        else:
            print('insta_id not found')

    def sync_following(self):
        profile = self.get_profile_info(self.account_name, 'following')
        if profile is not None:
            # followerButtom = self.driver.find_elements(By.XPATH, "//*[@class='_aacl _aacp _aacu _aacx _aad6 _aade']")[2]
            # followerButtom.click()

            time.sleep(2)  # loading following
            tempScrollHeight = self.driver.execute_script(
                "return document.getElementsByClassName('_aano')[0].scrollHeight")
            while True:
                # scroll down
                self.driver.execute_script(
                    "document.getElementsByClassName('_aano')[0].scrollTop = "
                    "document.getElementsByClassName('_aano')[0].scrollHeight")
                time.sleep(3)  # scrolldown ediltikden sonra yuklemeyi bekliyoruz.
                scrollHeight = self.driver.execute_script(
                    "return document.getElementsByClassName('_aano')[0].scrollHeight")
                if tempScrollHeight == scrollHeight:  # ayni scrollheight sahip ise daha sona gidermiyor demektir.
                    print('ended scroll down')
                    break
                else:
                    tempScrollHeight = scrollHeight

            time.sleep(2)  # loading network
            responses = self.read_network_logs(
                self.url + '/api/v1/friendships/' + str(profile['id']) + '/following/?count=12')
            usernames = ''
            for response in responses:
                for user in response['users']:
                    usernames += "'" + user['username'] + "',"
                    find_result = database_helper.find(
                        'following', "account_name='" + self.account_name + "' AND username='" + user['username'] + "'",
                        'id,username')
                    if find_result is None:
                        database_helper.insert('following', {
                            'account_name': self.account_name,
                            'insta_id': user['pk'],
                            'username': user['username'],
                            'full_name': user['full_name'],
                            'is_verified': user['is_verified'],
                            'profile_pic_url': user['profile_pic_url']
                        }, True)
                    else:
                        database_helper.update('following', 'id=' + str(find_result['id']), {
                            'account_name': self.account_name,
                            'insta_id': user['pk'],
                            'username': user['username'],
                            'full_name': user['full_name'],
                            'is_verified': user['is_verified'],
                            'profile_pic_url': user['profile_pic_url']
                        })
            if usernames != '':
                usernames = usernames.rstrip(',')
                database_helper.delete(
                    'following', "account_name='" + self.account_name + "' AND username NOT IN(" + usernames + ")")

            print('synchronized following')
        else:
            print('profile id not found')

    def following_compare_to_followers(self):
        whitelist = database_helper.find_all('whitelist', 'id,username', "account_name='" + self.account_name + "'")
        username_whitelist = ''
        for row in whitelist:
            username_whitelist += "'" + row['username'] + "',"
        if username_whitelist != '':
            username_whitelist = username_whitelist.rstrip(',')
        else:
            username_whitelist = "''"

        following = database_helper.find_all('following', 'id, username', "username NOT IN(" + username_whitelist + ")")
        for follow in following:
            find_result = database_helper.find(
                'followers', "account_name='" + self.account_name + "' AND username='" + follow['username'] + "'",
                'id,username')
            if find_result is None:
                print(follow['username'])


if __name__ == '__main__':
    # try:
    logging.basicConfig(filename='process.log', encoding='utf-8', level=logging.INFO)
    insta = InstaDiscover()

    insta.login()
    insta.sync_followers()
    insta.sync_following()
    insta.following_compare_to_followers()
    # while True:
    #     for i in range(1, 2, 1):
    #         insta.discover()
    #         time.sleep(2)
    #     insta.check_up_users()
    #     time.sleep(2)
    insta.close_browser()

    # except Exception:
    #     logging.exception("message")

    ### TEST

    # row = database_helper.find('discover_users', 'id=151')
    # database_helper.update('discover_users', 'id=' + str(row['id']), {
    #     'expires_at': '2021-12-11 12:11:05'
    # })
