from flask import Flask
from config import Config, db, migrate
from flask_login import LoginManager
from flask_wtf import CSRFProtect

app = Flask(__name__)
app.config.from_object(Config)

# --- Database setup ---
db.init_app(app)
migrate.init_app(app, db)

# --- Flask login setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

csrf = CSRFProtect(app)

# Import routes after app initialization to avoid circular imports
from routes import *

if __name__ == "__main__":
    app.run(debug=True)
