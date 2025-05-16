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
        submit_button = form.find_element(By.CSS_SELECTOR, "button.auth-btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Wait for redirect and verify successful login
        time.sleep(1)  # Wait for redirect
        self.assertIn("/", self.driver.current_url)

    def test_share_data(self):
        # Create two users
        self.create_user("oak", "oak@email.com", "pokemon")
        self.create_user("elm", "elm@email.com", "totodile")
        
        # Login as first user
        self.driver.get(localhost + "/login")
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        username_input = form.find_element(By.NAME, "username")
        username_input.send_keys("oak")
        password_input = form.find_element(By.NAME, "password")
        password_input.send_keys("pokemon")
        submit_button = form.find_element(By.CSS_SELECTOR, "button.auth-btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Navigate to share page
        time.sleep(1)
        self.driver.get(localhost + "/network")
        
        # Wait for share form
        share_form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "share-form"))
        )
        
        # Enter username to share with
        share_input = share_form.find_element(By.NAME, "share_username")
        share_input.send_keys("elm")
        
        # Submit share form
        submit_button = share_form.find_element(By.CSS_SELECTOR, "button[type='submit']")
        self.driver.execute_script("arguments[0].click();", submit_button)
        
        # Verify success message
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        self.assertIn("Data shared successfully", self.driver.page_source)

    def test_signup_flow(self):
        self.driver.get(localhost + "/signup")
        
        # Wait for form and find elements
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        
        # Fill in signup form
        username = "newuser123"
        email = "newuser@test.com"
        password = "testpass123"
        
        username_input = form.find_element(By.NAME, "username")
        username_input.send_keys(username)
        
        email_input = form.find_element(By.NAME, "email")
        email_input.send_keys(email)
        
        password_input = form.find_element(By.NAME, "password")
        password_input.send_keys(password)
        
        confirm_input = form.find_element(By.NAME, "confirm_password")
        confirm_input.send_keys(password)
        
        # Submit form
        submit_button = form.find_element(By.CSS_SELECTOR, "button.auth-btn")
        self.driver.execute_script("arguments[0].click();", submit_button)
        
        # Wait for redirect and success message
        WebDriverWait(self.driver, 10).until(
            EC.url_contains("/login")
        )
        self.assertIn("Account created successfully", self.driver.page_source)

    def test_share_and_view_data(self):
        # Create two users
        self.create_user("oak", "oak@email.com", "pokemon")
        self.create_user("elm", "elm@email.com", "totodile")
        
        # Login as first user (oak)
        self.driver.get(localhost + "/login")
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        username_input = form.find_element(By.NAME, "username")
        username_input.send_keys("oak")
        password_input = form.find_element(By.NAME, "password")
        password_input.send_keys("pokemon")
        submit_button = form.find_element(By.CSS_SELECTOR, "button.auth-btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Upload some data first
        self.driver.get(localhost + "/upload")
        upload_form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-form"))
        )
        
        # Enter showdown username and replay
        showdown_input = upload_form.find_element(By.NAME, "username")
        showdown_input.send_keys("oak")
        replay_input = upload_form.find_element(By.NAME, "replay_0")
        replay_url = "https://replay.pokemonshowdown.com/gen9vgc2025regg-2334903558-e5u8i2vynqi66x9hou3wl4fxix7kimfpw"
        replay_input.send_keys(replay_url)
        submit_button = upload_form.find_element(By.CSS_SELECTOR, "button.generate-btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Navigate to network page to share
        self.driver.get(localhost + "/network")
        network_form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "network-form"))
        )
        
        # Share with elm
        search_input = network_form.find_element(By.NAME, "search_user")
        search_input.send_keys("elm")
        submit_button = network_form.find_element(By.CSS_SELECTOR, "button.btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Verify sharing success
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "flash"))
        )
        self.assertIn("Data shared successfully", self.driver.page_source)

        # Logout
        self.driver.get(localhost + "/logout")

        # Login as second user (elm)
        self.driver.get(localhost + "/login")
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        username_input = form.find_element(By.NAME, "username")
        username_input.send_keys("elm")
        password_input = form.find_element(By.NAME, "password")
        password_input.send_keys("totodile")
        submit_button = form.find_element(By.CSS_SELECTOR, "button.auth-btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Go to visualise page
        self.driver.get(localhost + "/visualise")
        
        # Select oak's shared data
        visualise_form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "network-form"))
        )
        shared_user_input = visualise_form.find_element(By.NAME, "shared_user")
        shared_user_input.send_keys("oak")
        submit_button = visualise_form.find_element(By.CSS_SELECTOR, "button.btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Verify oak's data is visible
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "replay-record"))
        )
        self.assertIn("gen9vgc2025regg-2334903558", self.driver.page_source)

    def test_upload_and_visualize(self):
        # Login first
        self.create_user("xXFortniteGamerXx", "fortnite@email.com", "victory_royale")
        self.driver.get(localhost + "/login")
        
        form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "form"))
        )
        username_input = form.find_element(By.NAME, "username")
        username_input.send_keys("xXFortniteGamerXx")
        password_input = form.find_element(By.NAME, "password")
        password_input.send_keys("victory_royale")
        submit_button = form.find_element(By.CSS_SELECTOR, "button.auth-btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Wait for login and navigate to upload
        time.sleep(1)
        self.driver.get(localhost + "/upload")
        
        upload_form = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "upload-form"))
        )
        
        showdown_input = upload_form.find_element(By.NAME, "username")
        showdown_input.send_keys("xXFortniteGamerXx")

        replay_input = upload_form.find_element(By.NAME, "replay_0")
        replay_url = "https://replay.pokemonshowdown.com/gen9vgc2025regg-2334903558-e5u8i2vynqi66x9hou3wl4fxix7kimfpw"
        replay_input.send_keys(replay_url)

        submit_button = upload_form.find_element(By.CSS_SELECTOR, "button.generate-btn")
        self.driver.execute_script("arguments[0].click();", submit_button)

        # Wait for processing and verify data appears
        time.sleep(2)
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
