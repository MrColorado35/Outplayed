# This is a sample Python script.
# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
from time import sleep
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import selenium.common.exceptions as EX
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from random import randrange
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service # as ChromeService
from datetime import datetime, timedelta, timezone



class Outplayed:
    # assign default parameters while calling the app for the first time
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client.Outplayed
        # self.error = False
        self.params = ({'in_progress': 0, 'failed': 0, 'complete': 0})
        self.driver = self.start_driver()
        self.main_url = "https://sports.bwin.com/"

    # Create the driver
    @staticmethod
    def start_driver(pictures=False):
        # Create ChromeOptions instance
        service = Service()
        options = webdriver.ChromeOptions()
        # Adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")
        # Exclude the collection of enable-automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        if not pictures:
            # Do not download images
            options.add_argument('--blink-settings=imagesEnabled=false')

        # Turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)
        # Old version of the driver creation in case if the latest version won't work (This tends to happen after an update to the browser)
        # driver = webdriver.Chrome(options=options, service=ChromeService(ChromeDriverManager(version="114.0.5735.16").install()))
        driver = webdriver.Chrome(service=service, options=options)
        return driver

    def get_tennis(self):
        btn_tennis = self.driver.find_element(By.XPATH, "//div[contains(@class, 'main-items')]//vn-menu-item//a[contains(text(), 'Tennis')]")
        btn_tennis.click()
        sleep(4)
        btn_all = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ms-top-items-widget')]//div[contains(@class, 'list-all')]//a[contains(@class, 'ms-active-highlight')][1]")
        btn_all.click()
        sleep(5)
        print("Got to the 'all competitions' page ")

    def get_competitions(self):




if __name__ == '__main__':
    print('Hello, I hope you had a lovely day')
    app = Outplayed()
    app.driver.get(app.main_url)
    sleep(8)
    app.get_tennis()
