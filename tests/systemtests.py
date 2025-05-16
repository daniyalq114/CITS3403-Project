import unittest
import time
import multiprocessing

from app import create_app, db
from app.config import TestConfig
from app.models import User

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

localhost = "http://localhost:5000"


class SystemTests(unittest.TestCase):
    def setUp(self):
        # Setup Flask app and database
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Start Flask server in a separate process
        self.server_thread = multiprocessing.Process(target=self.app.run, kwargs={"use_reloader": False})
        self.server_thread.start()
        time.sleep(1)  # Give server time to start

        # Setup Selenium WebDriver (ensure geckodriver is in PATH)
        self.driver = webdriver.Firefox()

    def tearDown(self):
        # Clean up database and shutdown server
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.driver.quit()
        self.server_thread.terminate()

    def create_user(self, username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    def test_login_page(self):
        # Pre-create user in the database
        self.create_user("ltsurge", "ltsurge@email.com", "electrode")

        # Visit login page
        self.driver.get(localhost + "/login")

        # Wait for username input field
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )

        # Fill login form
        username_input = self.driver.find_element(By.NAME, "username")
        username_input.send_keys("ltsurge")

        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys("electrode")

        submit_button = self.driver.find_element(By.NAME, "submit")
        submit_button.click()

        # Example verification: check if redirected to homepage or dashboard
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Optionally verify page contains a logout link or username display
        page_source = self.driver.page_source
        self.assertIn("ltsurge", page_source)


if __name__ == "__main__":
    unittest.main()
