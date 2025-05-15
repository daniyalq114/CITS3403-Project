from app.config import TestConfig
from app import , db
from selenium import webdriver

class SystemTests(unittest.TestCase):
    def setUp(self):
        self.app = (TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Set up Selenium WebDriver
        self.driver = webdriver.Chrome()  # or any other driver you prefer

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        self.driver.quit()  # Close the browser after tests

    def test_home_page(self):
        self.driver.get(self.app.config['SERVER_NAME'] + '/')
        self.assertIn("Welcome to the Pokemon Battle App", self.driver.page_source)