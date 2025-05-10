import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
default_database_location = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "instance", "app.db")
    SECRET_KEY = os.getenv('SECRET_KEY')