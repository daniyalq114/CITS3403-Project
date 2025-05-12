import unittest

from flask import url_for
from app import create_app, db
from config import TestConfig

test_app = create_app(TestConfig)