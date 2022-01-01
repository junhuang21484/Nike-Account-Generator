import time
from generator import Controller


class Manager:
    def main_menu(self):
        choice = input("\nMain Menu\n"
                       "[1] Task Menu\n"
                       "[2] Setting Menu\n"
                       "[E] Exit").upper()

        if choice == "1":
            self.task_menu()
        elif choice == "2":
            print("Coming soon...")
            self.main_menu()
        elif choice == "E":
            print("Exiting after 3 seconds...")
            time.sleep(3)

    def task_menu(self):
        choice = input("\nTask Menu\n"
                       "[1] Start Task\n"
                       "[B] Back to main menu").upper()

        if choice == "1":
            browser_amount = input("How many browser you want: ")
            task_per_browser = input("How many accounts you want each browser to generate: ")
            task_controller = Controller(int(browser_amount), int(task_per_browser))
            task_controller.start()

            self.main_menu()

        elif choice == "B":
            self.main_menu()

        else:
            print("UNKNOWN RESPONSE TRY AGAIN!")
            self.task_menu()


if __name__ == '__main__':
    manager = Manager()
    manager.main_menu()
