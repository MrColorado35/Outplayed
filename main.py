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


class Outplayed:
    # assign default parameters while calling the app for the first time
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client.Outplayed
        # self.error = False
        self.params = ({'in_progress': 0, 'failed': 0, 'complete': 0})
        self.driver = self.start_driver()
        self.main_url = ""

    def start_driver(self):
        pass



if __name__ == '__main__':
    print('Hello, I hope you had a lovely day')
