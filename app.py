from flask_migrate import Migrate
from app import create_app, db
from config import DeploymentConfig
from app.models import User, Match, Team, TeamPokemon, MoveUsage

app = create_app(DeploymentConfig)
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Match': Match, 'Team': Team, 'TeamPokemon': TeamPokemon, 'MoveUsage': MoveUsage}

if __name__ == "__main__":
    app.run(debug=True)
