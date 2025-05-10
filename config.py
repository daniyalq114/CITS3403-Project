import os

basedir = os.path.abspath(os.path.dirname(__file__))
instance_dir = os.path.join(basedir, 'instance')
default_database_location = 'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "instance", "app.db")
    SECRET_KEY = os.getenv('SECRET_KEY')