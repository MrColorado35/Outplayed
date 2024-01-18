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

    # Once you are on the right page, press two buttons to get to teh required data
    def get_tennis(self):
        # Find required button
        btn_tennis = self.driver.find_element(By.XPATH, "//div[contains(@class, 'main-items')]//vn-menu-item//a[contains(text(), 'Tennis')]")
        # Simulate clicking
        btn_tennis.click()
        # Allow the page to load
        sleep(4)
        # Repeat last 3 steps with another button
        btn_all = self.driver.find_element(By.XPATH, "//div[contains(@class, 'ms-top-items-widget')]//div[contains(@class, 'list-all')]//a[contains(@class, 'ms-active-highlight')][1]")
        btn_all.click()
        sleep(5)
        # inform the Programmer about the success
        print("Got to the 'all competitions' page ")

    # Collect details about competitions
    def get_competitions(self):

        pass

    # collect details about the time
    def get_time(self, time_text):
        # Get the current UTC time
        current_utc_time = datetime.utcnow()

        # Parse the input time
        event_time_str = time_text
        event_time = datetime.strptime(event_time_str, "%Y-%m-%d %I:%M %p")

        # Calculate the time difference between now and the event time
        time_difference = event_time - current_utc_time

        # If the event is today, add 1 day to the event time
        if time_difference.days == 0 and time_difference.seconds < 0:
            event_time += timedelta(days=1)
        # Print the event time in the desired format (yyyy-mm-dd hh:mm)
        formatted_event_time = event_time.strftime("%Y-%m-%d %H:%M")
        return formatted_event_time, current_utc_time





if __name__ == '__main__':
    print('Hello, I hope you had a lovely day')
    app = Outplayed()
    app.driver.get(app.main_url)
    sleep(8)
    app.get_tennis()
