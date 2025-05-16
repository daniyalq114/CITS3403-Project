import os

basedir = os.path.abspath(os.path.dirname(__file__))
instance_db_path = os.path.join(basedir, "instance", "app.db")

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{instance_db_path}"
    SECRET_KEY = os.getenv('SECRET_KEY')

class DeploymentConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + instance_db_path

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    SERVER_NAME = 'localhost.localdomain'  
    APPLICATION_ROOT = '/'                 
    PREFERRED_URL_SCHEME = 'http'          
