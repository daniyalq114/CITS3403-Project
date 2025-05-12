from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    csrf = CSRFProtect(app)
    return app

# Import routes after app initialization to avoid circular imports
from routes import *

if __name__ == "__main__":
    app.run(debug=True)
