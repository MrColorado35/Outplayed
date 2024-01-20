from time import sleep
from selenium.webdriver.common.by import By
from pymongo import MongoClient
import selenium.common.exceptions as EX
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from datetime import datetime, timedelta, timezone
from fractions import Fraction


class Outplayed:
    # assign default parameters while calling the app
    def __init__(self):
        # Connect to your local MongoDB
        self.client = MongoClient("mongodb://localhost:27017/")
        # Create a collection in your database
        self.db = self.client.Outplayed
        # Create the driver
        self.driver = self.start_driver()
        # First version was designed to go through several click elements, but then to cat it short I changed it to go straight where we want to be.
        # self.main_url = "https://sports.bwin.com/"
        self.main_url = "https://sports.bwin.com/en/sports/tennis-5/betting/grand-slam-tournaments-5"

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

    # Once you are on the right page, press two buttons to get to the required data
    # Also, xpath selectors here are wrong, I really don't want to spend too much time on fixing this part if it's not necessary
    def get_tennis(self):
        # Find required button
        btn_tennis = self.driver.find_element(By.XPATH,
                                              "//div[contains(@class, 'main-items')]//vn-menu-item//a[contains(text(), 'Tennis')]")
        # Simulate clicking
        btn_tennis.click()
        # Allow the page to load
        sleep(4)
        # Repeat last 3 steps with another button
        btn_all = self.driver.find_element(By.XPATH,
                                           "//div[contains(@class, 'ms-top-items-widget')]//div[contains(@class, 'list-all')]//a[contains(@class, 'ms-active-highlight')][1]")
        btn_all.click()
        sleep(5)
        # inform the Programmer about the success
        print("Got to the 'all competitions' page ")

    # Collect details about the competitions
    def get_competitions(self):
        # focus on the right set of data
        competitions = self.driver.find_elements(By.CSS_SELECTOR,
                                                 'ms-grid[sortingtracking="Competitions"] .event-group')
        # iterate through all groups, no matter the number
        for competition in competitions:
            # Get the name for each competition
            tournament_name = competition.find_element(By.CSS_SELECTOR, ' ms-league-header.league-group').text
            # get data set for each competition
            details = competition.find_elements(By.CSS_SELECTOR, "ms-event.grid-event")
            # iterate through every event details
            for detail in details:
                try:
                    # Get the event name in the required format
                    players = detail.find_elements(By.CSS_SELECTOR, "div.participants-pair-game div.participant")
                    player_list = [player.text for player in players if players != ""]
                    print(player_list)

                    # if len(player_list) > 0:

                    player_a = player_list[0]
                    player_b = player_list[1]
                    event_name = f"{player_a} v {player_b}"
                    print(event_name)
                except Exception as e:
                    print(e)
                    players, player_list, event_name, player_b, player_a = "", "", "", "", ""
                    print("Cannot access Plyer name!")

                # Get the event time in the required format
                try:
                    event_time = detail.find_element(By.CSS_SELECTOR, ".grid-event-timer .starting-time").text
                    exact_time = self.get_time(event_time)
                except EX.NoSuchElementException:
                    exact_time = detail.find_element(By.CSS_SELECTOR, ".grid-event-info").text
                except Exception as e:
                    print(e)
                    exact_time = ""
                    print("Failed to collect time")

                # Get current time in UTC
                time_now = datetime.utcnow()

                try:
                    all_odds = detail.find_elements(By.CSS_SELECTOR, "ms-option div.option-indicator")
                    odds = [odd.text for odd in all_odds if all_odds != 0]
                    odd_a = odds[0]  # self.calculate_odds(odds[0])
                    print(f"Odd a is equal to: {odd_a}")
                    odd_b = odds[1]  # self.calculate_odds(odds[1])
                    print(f"Odd b is equal to: {odd_b}")
                    decimal_odd_a = self.calculate_odds(odd_a)
                    decimal_odd_b = self.calculate_odds(odd_b)
                except Exception as e:
                    print(e)
                    print("Failed to collect odds")
                    odds = []

                try:
                    details = {
                        "tournament_name": tournament_name,
                        "last_fetched": time_now,
                        "events": [
                            {
                                "event_name": event_name,
                                "start_time": exact_time,
                                "outcomes": [
                                    {
                                        "outcome_name": player_a,
                                        "odds": decimal_odd_a
                                    },
                                    {
                                        "outcome_name": player_b,
                                        "odds": decimal_odd_b
                                    }
                                ]
                            }
                        ]

                    }
                    for k, v in details.items():
                        print(f'{k} = {v}')

                    # send details to MongoDB. "data" will be a name of table inside your database collection
                    self.db.data_v7.update_one({"tournament_name": tournament_name, "last_fetched": time_now},
                                            {'$set': details}, upsert=True)
                except:
                    print("Failed to collect required data, have a look at it tomorrow Stan, you are too tired")

    def calculate_odds(self, fractional_odds):
        try:
            # Parse the fractional odds
            odds = Fraction(fractional_odds)

            # Convert to decimal format and round to two decimal places
            decimal_odds = round(float(odds) + 1, 2)

            return decimal_odds
        except ValueError:
            print("Invalid input format. Please provide odds in the form 'a/b'.")



    def get_time(self, time_text):
        # Get the current UTC time
        current_utc_time = datetime.utcnow()

        # Parse the input time
        event_time = None
        if "Tomorrow" in time_text:
            # Extract the time part (e.g., "12:15 AM")
            time_part = time_text.split("Tomorrow / ")[1]

            # Combine with tomorrow's date
            event_time_str = f"{(current_utc_time + timedelta(days=1)).strftime('%Y-%m-%d')} {time_part}"

            # Parse the combined datetime
            event_time = datetime.strptime(event_time_str, "%Y-%m-%d %I:%M %p")
        elif "Today" in time_text:
            # Extract the time part (e.g., "9:15 PM")
            time_part = time_text.split("Today / ")[1]

            # Combine with today's date
            event_time_str = f"{current_utc_time.strftime('%Y-%m-%d')} {time_part}"

            # Parse the combined datetime
            event_time = datetime.strptime(event_time_str, "%Y-%m-%d %I:%M %p")

        else:
            # Parse the input time for today
            event_time = datetime.strptime(time_text, "%Y-%m-%d %I:%M %p")

        # Calculate the time difference between now and the event time
        time_difference = event_time - current_utc_time

        # If the event is today, add 1 day to the event time
        if time_difference.days == 0 and time_difference.seconds < 0:
            event_time += timedelta(days=1)

        # Print the event time in the desired format (yyyy-mm-dd hh:mm)
        formatted_event_time = event_time.strftime("%Y-%m-%d %H:%M")
        return formatted_event_time

    # Find and close cookies message
    def accept_cookies(self):

        cookies_btn  = self.driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler")
        cookies_btn.click()
        sleep(2)

    # Go through all tournaments
    def other_buttons(self):
        buttons = self.driver.find_elements(By.XPATH, "//ms-item-tree[contains(@class, 'all-competitions')]//ms-item[contains(@class, 'collapsed')]/a") #[position() >= 2]/a")
        # buttons = self.driver.find_elements(By.CSS_SELECTOR, "ms-item.active+ ms-item-tree a")
        for i in range(6):
            try:
                print("Searching for the button")
                btn = buttons[i]
                btn.click()
                print("Button clicked")
                sleep(3)
                self.btn_level_2()
                print(f"Completed collecting data for the competition number {i}")
            except Exception as e:
                print(e)
                print(f"Failed to collect data for the competition number {i}, have a look at it")
                sleep(24)

    # After going through expandable accordion, this function will click all links that contain "All" and collect the data from within them
    def btn_level_2(self):
        # second_click = self.driver.find_element(By.XPATH, "//ms-item-tree[contains(@class, 'all-competitions')]//ms-item[contains(@class, 'expanded')][last()]/following-sibling::ms-item-tree//a[1]")
        second_clicks = self.driver.find_elements(By.CSS_SELECTOR, "ms-item+ ms-item-tree.item-level-2 a.ms-active-highlight") #"ms-item.active + ms-item-tree a")
        for c in range(len(second_clicks)):
            second_click = second_clicks[c]
            if "All" in second_click.text:
                second_click.click()
                sleep(3)
                self.scroll_down()
                print("Scrolled down")
                self.get_competitions()
            else:
                continue

    def scroll_down(self, element=""):
        try:
            if element != "":
                print("scrolling to the element")
                #scroll down to the required element (It will be presented on top of the page, if possible)
                self.driver.execute_script("arguments[0].scrollIntoView();", element)
            else:
                print("Scrolling to the bottom of the page")
                # scroll down to the bottom of the page if no element was provided
                self.driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
        except:
            print("Cannot scroll for some reason")

if __name__ == '__main__':
    print('Hello, I hope you have a lovely day')
    app = Outplayed()
    app.driver.get(app.main_url)
    app.driver.maximize_window()
    sleep(12)
    # app.get_tennis()
    app.accept_cookies()
    app.get_competitions()
    print("page 1 collected")
    app.other_buttons()
    print("That's it my friend")
