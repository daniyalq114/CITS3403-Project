import unittest
from flask import url_for
from app import create_app, db
from config import TestConfig
from app.models import User, Match, Team, TeamPokemon, MoveUsage, SharedAccess  

class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_creation(self):
        u = User(username="ash", email="ash@email.com")
        u.set_password("pikachu")
        db.session.add(u)
        db.session.commit()
        self.assertEqual(u.username, "ash")

    def test_duplicate_username(self):
        u1 = User(username="misty", email="misty1@email.com")
        u1.set_password("starmie")
        db.session.add(u1)
        db.session.commit()
        
        u2 = User(username="misty", email="misty2@email.com")
        u2.set_password("psyduck")
        db.session.add(u2)
        with self.assertRaises(Exception):
            db.session.commit()

    def test_password_hashing(self):
        u = User(username="brock", email="brock@email.com")
        u.set_password("onix")
        self.assertFalse(u.check_password("geodude"))
        self.assertTrue(u.check_password("onix"))

class RoutesTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_public_routes(self):
        with self.app.test_request_context():
            # These routes should be accessible without login
            routes = ['main.index', 'main.login', 'main.signup']
            for route in routes:
                response = self.client.get(url_for(route))
                self.assertEqual(response.status_code, 200)

    def test_protected_routes_without_login(self):
        with self.app.test_request_context():
            # These routes should redirect to login when not authenticated
            protected_routes = ['main.upload', 'main.visualise', 'main.network']
            for route in protected_routes:
                response = self.client.get(url_for(route))
                self.assertEqual(response.status_code, 302)  # Redirect
                self.assertTrue('/login' in response.location)

    def test_protected_routes_with_login(self):
        with self.app.test_request_context():
            # Create and login a test user
            u = User(username="go", email="go@email.com")
            u.set_password("scorbunny")
            db.session.add(u)
            db.session.commit()

            # Login
            self.client.post(url_for('main.login'), data={
                'username': 'go',
                'password': 'scorbunny'
            }, follow_redirects=True)

            # Test protected routes
            protected_routes = ['main.upload', 'main.visualise', 'main.network']
            for route in protected_routes:
                response = self.client.get(url_for(route))
                self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials(self):
        with self.app.test_request_context():
            # Create test user
            u = User(username="chloe", email="chloe@email.com")
            u.set_password("yamper")
            db.session.add(u)
            db.session.commit()

            # Try logging in
            response = self.client.post(url_for('main.login'), data={
                'username': 'chloe',
                'password': 'yamper'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()