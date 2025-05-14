import unittest

from flask import url_for
from app import create_app, db
from config import TestConfig

class UnitTests(unittest.TestCase):
    def setUp(self):
        test_app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        add_test_data_to_db()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.app.test_client().get(url_for('main.index'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome to the Pokemon Battle App", response.data)
    
    def test_successful_signup(self):
        response = self.app.test_client().post(url_for('main.signup'), data={
            'username': 'testuser',
            'email': 'testuser@email.com',
            'password': 'testpassword',
            'confirm_password': 'testpassword'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, url_for('main.login', _external=True))
        with self.app.test_client() as client:
            response = client.get(url_for('main.login'))
            self.assertIn(b"Logged in successfully!", response.data)

    def test_successful_login(self):
        with self.app.test_client() as client:
            client.post(url_for('main.signup'), data={
                'username': 'testuser',
                'password': 'testpassword'
            })
            response = client.post(url_for('main.login'), data={
                'username': 'testuser',
                'password': 'testpassword'
            })
            self.assertEqual(response.status_code, 302)

