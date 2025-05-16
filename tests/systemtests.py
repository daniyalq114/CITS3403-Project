import unittest
import time
import subprocess
import os
import signal
from pathlib import Path

from app import create_app, db
from config import TestConfig
from app.models import User

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

localhost = "http://localhost:5000"


class SystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start Flask server as a separate process
        cls.server_process = subprocess.Popen(
            ["python3", "tests/test_server.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(2)  # Give server time to start

    @classmethod
    def tearDownClass(cls):
        # Shutdown the server
        os.kill(cls.server_process.pid, signal.SIGTERM)
        cls.server_process.wait()

    def setUp(self):
        # Setup Flask app and database
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Setup Selenium WebDriver
        self.driver = webdriver.Firefox()

    def tearDown(self):
        # Clean up
        self.driver.quit()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def create_user(self, username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

    def test_login_page(self):
        # Pre-create user in the database
        self.create_user("ltsurge", "ltsurge@email.com", "electrode")

        # Visit login page and wait for it to load
        self.driver.get(localhost + "/login")
        
        # Wait for form and find elements
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        # Fill in login form
        username_input = form.find_element(By.NAME, "username")
        username_input.send_keys("ltsurge")

        password_input = form.find_element(By.NAME, "password")
        password_input.send_keys("electrode")

        # Find and click submit button within the form
        submit_button = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Wait for redirect and verify successful login
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(localhost + "/")  # Assuming successful login redirects to root
        )
        self.assertEqual(self.driver.current_url, localhost + "/")

    def test_upload_and_visualize(self):
        # Login first
        self.create_user("xXFortniteGamerXx", "fortnite@email.com", "victory_royale")
        self.driver.get(localhost + "/login")
        
        # Wait for form and find elements
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        username_input = form.find_element(By.NAME, "username")
        username_input.send_keys("xXFortniteGamerXx")
        password_input = form.find_element(By.NAME, "password")
        password_input.send_keys("victory_royale")
        submit_button = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Wait for redirect and then navigate to upload page
        WebDriverWait(self.driver, 10).until(
            EC.url_to_be(localhost + "/")
        )
        self.driver.get(localhost + "/upload")
        
        # Wait for form elements
        upload_form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-form"))
        )
        
        # Enter showdown username
        showdown_input = upload_form.find_element(By.NAME, "username")
        showdown_input.send_keys("xXFortniteGamerXx")

        # Enter replay URL
        replay_url = "https://replay.pokemonshowdown.com/gen9vgc2025regg-2334903558-e5u8i2vynqi66x9hou3wl4fxix7kimfpw"
        replay_input = upload_form.find_element(By.CSS_SELECTOR, "input[type='url']")
        replay_input.send_keys(replay_url)

        # Submit form
        submit_button = upload_form.find_element(By.CSS_SELECTOR, "button.generate-btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Wait and navigate to visualise page
        time.sleep(1)  # Allow time for processing
        self.driver.get(localhost + "/visualise")
        
        # Wait for content to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "main"))
        )
        self.assertIn("gen9vgc2025regg-2334903558", self.driver.page_source)

    def test_navigation_flow(self):
        # Create and login user
        self.create_user("misty", "misty@email.com", "starmie")
        self.driver.get(localhost + "/login")
        
        # Wait for form and login
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        username_input = form.find_element(By.NAME, "username")
        username_input.send_keys("misty")
        password_input = form.find_element(By.NAME, "password")
        password_input.send_keys("starmie")
        submit_button = form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Test navigation
        nav_links = ["/upload", "/visualise", "/network"]
        for link in nav_links:
            self.driver.get(localhost + link)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "main"))
            )
