import random
import string
import names
import datetime
import json

# from multiprocessing import Process
from playwright.sync_api import sync_playwright


class Helper:
    def __init__(self, target_num, max_browser):
        self.target_num = target_num
        self.max_browser = max_browser

        self.total_browser = 0
        self.running_browser = 0
        self.amount_gen = 0

        self.file_location = "accounts.txt"

    def get_amount_gen(self):
        return self.amount_gen

    def get_total_browser(self):
        return self.total_browser

    def subtract_running_browser(self):
        self.running_browser -= 1

    def add_running_browser(self):
        self.running_browser += 1

    def add_amount_gen(self):
        self.amount_gen += 1

    def add_total_browser(self):
        self.total_browser += 1

    def check_can_create(self):
        return self.running_browser < self.max_browser and self.running_browser < self.target_num

    def check_target_reached(self):
        return (self.target_num - self.amount_gen) <= 0

    def check_browser_running(self):
        return self.running_browser != 0

    def write_heading(self):
        with open(self.file_location, "a", encoding="UTF-8") as f:
            f.write(f"\n{'=' * 35} STARTED {datetime.datetime.now()} {'=' * 35}\n")

    def write_account(self, acc_info):
        with open(self.file_location, "a+", encoding="UTF-8") as f:
            f.write(f"{acc_info}\n")

    def write_ending(self):
        with open(self.file_location, "a", encoding="UTF-8") as f:
            f.write(f"\n{'*' * 106}\n")


class Controller:
    def __init__(self, target_num):
        self.target_num = target_num

        self.setting = json.load(open("setting.json", "r", encoding="UTF-8"))
        self.helper = Helper(target_num, self.setting["controller"]["max_browser"])

    @staticmethod
    def get_random_info():
        gender = random.choice(["male", "female"])
        first_name = names.get_first_name(gender=gender)
        last_name = names.get_last_name()
        dob = str(random.randint(1, 12)).rjust(2, '0') + str(random.randint(1, 28)).rjust(2, '0') + str(random.randint(1975, 2002))
        email = first_name + last_name + ''.join(random.choices(string.ascii_lowercase, k=2)) + str(random.randint(1, 999)) + "@gmail.com"
        password = first_name + last_name + str(random.randint(1000, 99999)) + random.choice(string.punctuation)
        return [email, password, first_name, last_name, dob, gender]

    def start(self):
        gen_setting = self.setting['generator']
        min_tdelay = gen_setting["min_type_delay"]
        max_tdelay = gen_setting["max_type_delay"]
        min_sdelay = gen_setting["min_submit_delay"]
        max_sdelay = gen_setting["max_submit_delay"]

        self.helper.write_heading()
        while True:
            if self.helper.check_can_create() and not self.helper.check_target_reached():
                browser_id = self.helper.get_total_browser()
                user_info = self.get_random_info()

                browser = Browser(self.helper, browser_id, user_info, min_tdelay, max_tdelay, min_sdelay, max_sdelay)
                # task = Process(target=browser.start_process)
                # task.start()

                browser.start_process()

                self.helper.add_total_browser()
                self.helper.add_running_browser()

            if self.helper.check_target_reached():
                print("Required amount of account reached, will exit the program when all browsers close up!")
                break

        while True:
            if not self.helper.check_browser_running():
                self.helper.write_ending()
                print(f"The generation process has now ended! "
                      f"{self.helper.get_amount_gen()} accounts has been generated!")
                break


class Browser:
    def __init__(self, helper: Helper, browser_id, user_info, min_type_delay, max_type_delay, min_submit_delay, max_submit_delay):
        self.helper = helper
        self.browser_id = browser_id
        self.user_info = user_info
        self.min_type_delay = min_type_delay
        self.max_type_delay = max_type_delay
        self.min_submit_delay = min_submit_delay
        self.max_submit_delay = max_submit_delay

        self.page = None

    def print_log(self, msg):
        print(f"[{datetime.datetime.now()}] (Browser {self.browser_id}): {msg}")

    def fill_info(self):
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

            selc.type(self.user_info[i], delay=random.randint(self.min_type_delay, self.max_type_delay))
            selc.press("Tab")

    def finish_buttons(self):
        self.print_log("Finishing registering")
        # Select gender
        gender = "//span[text()='Male']" if self.user_info[-2] == "male" else "//span[text()='Female']"
        selc = self.page.query_selector(gender)
        selc.hover()
        selc.click()

        self.page.wait_for_timeout(random.randint(self.min_submit_delay, self.max_submit_delay))

        # Click join
        selc = self.page.query_selector("//input[@value='JOIN US']")
        selc.hover()
        selc.click()

    def start_process(self):
        with sync_playwright() as p:
            self.print_log("Starting browser")
            # Start browser
            browser = p.firefox.launch(headless=False)
            self.page = browser.new_page()
            self.print_log("Going to registering site")
            self.page.goto("https://www.nike.com/register", wait_until='commit')

            # Fill info
            self.fill_info()
            self.finish_buttons()

            self.print_log("Waiting for register to finish")
            self.page.wait_for_url("https://www.nike.com/")
            self.print_log("Successfully created an account")

            self.helper.write_account(f"{self.user_info[0]}:{self.user_info[1]}")
            self.helper.add_amount_gen()
            self.helper.subtract_running_browser()

            browser.close()


if __name__ == '__main__':
    tn = int(input("Enter target account number: "))
    controller = Controller(tn)
    controller.start()
