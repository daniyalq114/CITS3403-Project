from flask_migrate import Migrate
from app import create_app, db
from config import DeploymentConfig
import sqlite3
import os
from app.models import User, Match, Team, Pokemon, Moves

app = create_app(DeploymentConfig)

if__name__ == "__main__":
    app.run(debug=True)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Match': Match, 'Team': Team, 'Pokemon': Pokemon, 'Moves': Moves}