from flask import Flask
from config import Config
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprint
    from app.blueprints import main
    app.register_blueprint(main)
    
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    csrf = CSRFProtect(app)

    return app

if __name__ == "__main__":
    app = ()
    app.run(debug=True)
