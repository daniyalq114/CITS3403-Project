import unittest
import time
import multiprocessing

from app import create_app, db
from app.config import TestConfig
from app.models import User, Match, Team, TeamPokemon, MoveUsage

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

localhost = "http://localhost:5000"

class SystemTests(unittest.TestCase):
    def setUp(self):
        self.test_app = (TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        self.server_thread = multiprocessing.Process(target=)

        self.driver = webdriver.Firefox()  

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.driver.quit()  

    def create_user(self, username, email, password):
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
    
    def test_login_page(self):
        trainer1 = User(username="lt.surge", email="ltsurge@email,com", password="electrode")

        self.driver.get(localhost + "/login")
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located((By.NAME, "username"))
        )
        username_input = self.driver.find_element(By.NAME, "Username")
        username_input.send_keys(trainer1.username)
        user_email_input = self.driver.find_element(By.NAME, "User Email")
        user_email_input.send_keys(trainer1.email)
        password_input = self.driver.find_element(By.NAME, "Password")
        password_input.send_keys(trainer1.password)
        confirm_password_input = self.driver.find_element(By.NAME, "Confirm Password")
        confirm_password_input.send_keys(trainer1.password)
        submit_button = self.driver.find_element(By.NAME, "submit")
        submit_button.click()
        time.sleep(2)
        
        

