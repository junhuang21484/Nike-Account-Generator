import random
import string
import names
import datetime
import json
import time

from multiprocessing import Process
from playwright.sync_api import sync_playwright


FILE_LOCATION = "accounts.txt"


def write_heading():
    with open(FILE_LOCATION, "a", encoding="UTF-8") as f:
        f.write(f"\n{'=' * 35} STARTED {datetime.datetime.now()} {'=' * 35}\n")


def write_account(acc_info):
    with open(FILE_LOCATION, "a+", encoding="UTF-8") as f:
        f.write(f"{acc_info}\n")


def write_ending():
    with open(FILE_LOCATION, "a", encoding="UTF-8") as f:
        f.write(f"\n{'*' * 106}\n")


class Controller:
    def __init__(self, browser_amount, account_per_browser):
        self.browser_amount = browser_amount
        self.account_per_browser = account_per_browser

        self.setting = json.load(open("setting.json", "r", encoding="UTF-8"))

    def start(self):
        gen_setting = self.setting['generator']
        min_tdelay = gen_setting["min_type_delay"]
        max_tdelay = gen_setting["max_type_delay"]
        min_sdelay = gen_setting["min_submit_delay"]
        max_sdelay = gen_setting["max_submit_delay"]

        running_browsers = []

        write_heading()
        for browser_id in range(1, self.browser_amount + 1):
            browser = Browser(browser_id, self.account_per_browser, min_tdelay, max_tdelay, min_sdelay, max_sdelay)
            task = Process(target=browser.start_process)
            task.start()
            running_browsers.append(task)

            time.sleep(1)

        for task in running_browsers:
            task.join()

        write_ending()


class Browser:
    def __init__(self, browser_id, account_needed, min_type_delay, max_type_delay, min_submit_delay, max_submit_delay):
        self.browser_id = browser_id
        self.account_needed = account_needed
        self.min_type_delay = min_type_delay
        self.max_type_delay = max_type_delay
        self.min_submit_delay = min_submit_delay
        self.max_submit_delay = max_submit_delay

        self.page = None

        self.generated_account = 0

    @staticmethod
    def get_random_info():
        gender = random.choice(["male", "female"])
        first_name = names.get_first_name(gender=gender)
        last_name = names.get_last_name()
        dob = str(random.randint(1, 12)).rjust(2, '0') + str(random.randint(1, 28)).rjust(2, '0') + str(
            random.randint(1975, 2002))
        email = first_name + last_name + ''.join(random.choices(string.ascii_lowercase, k=2)) + str(
            random.randint(1, 999)) + "@gmail.com"
        password = first_name + last_name + str(random.randint(1000, 99999)) + random.choice(string.punctuation)
        return [email, password, first_name, last_name, dob, gender]

    def print_log(self, msg):
        print(f"[{datetime.datetime.now()}] (Browser {self.browser_id}): {msg}")

    def fill_info(self, user_info):
        elements = [
            '//input[@placeholder="Email address"]',  # Email
            '//input[@placeholder="Password"]',  # Password
            '//input[@placeholder="First Name"]',  # First name
            '//input[@placeholder="Last Name"]',  # Last name
            '//input[@placeholder="Date of Birth"]'  # DOB
        ]
        self.print_log("Waiting for site to load")
        self.page.wait_for_selector(elements[0])

        self.print_log("Filling user info")
        for i, ele in enumerate(elements):
            selc = self.page.query_selector(ele)
            selc.hover()
            if i == 0 or 4:
                selc.click()

            selc.type(user_info[i], delay=random.randint(self.min_type_delay, self.max_type_delay))
            selc.press("Tab")

    def finish_buttons(self, sex):
        self.print_log("Finishing registering")
        # Select gender
        gender = "//span[text()='Male']" if sex == "male" else "//span[text()='Female']"
        selc = self.page.query_selector(gender)
        selc.hover()
        selc.click()

        self.page.wait_for_timeout(random.randint(self.min_submit_delay, self.max_submit_delay))

        # Click join
        selc = self.page.query_selector("//input[@value='JOIN US']")
        selc.hover()
        selc.click()

    def start_process(self):
        while self.generated_account < self.account_needed:
            user_info = self.get_random_info()
            self.print_log("Starting browser")
            with sync_playwright() as p:
                # Start browser
                browser = p.firefox.launch(headless=False)
                self.page = browser.new_page()
                self.print_log("Going to registering site")
                self.page.goto("https://www.nike.com/register", wait_until='commit')

                # Fill info
                self.fill_info(user_info)
                self.finish_buttons(user_info[-2])

                self.print_log("Waiting for register to finish")
                self.page.wait_for_url("https://www.nike.com/")
                self.print_log("Successfully created an account")

                self.generated_account += 1

                write_account(user_info[0] + ":" + user_info[1])
                browser.close()