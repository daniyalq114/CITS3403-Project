import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

basedir = os.path.abspath(os.path.dirname(__file__))
instance_db_path = os.path.join(basedir, "instance", "app.db")

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{instance_db_path}"
    SECRET_KEY = os.getenv('SECRET_KEY')