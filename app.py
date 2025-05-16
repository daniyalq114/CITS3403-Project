from flask_migrate import Migrate
from app import create_app, db
from config import DeploymentConfig
import os

app = create_app(DeploymentConfig)

# Only import and run seed if in debug mode
if app.debug:
    try:
        from app.seed import seed_data
        with app.app_context():
            seed_data()
    except Exception as e:
        print(f"Seeding failed: {e}")

if __name__ == "__main__":
    app.run(debug=True)
