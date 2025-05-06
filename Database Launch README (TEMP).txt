Activate virtual env:
source lugi-venv/bin/activate

Setup flask:
export FLASK_APP=app.py

Enter flask shell:
flask shell

Enter these commands:

# Create db
from app import db, User, Match, Team

# Create a test user
u = User(username="ash", email="ash@kanto.com", password="pikachu123")
db.session.add(u)
db.session.commit()

# Test the user, output: [<User ash>]
User.query.all()

# Create a test match and team
m = Match(username="ash", match_id="match123", showdown_username="AshK", match_info="<html>test match</html>")
t = Team(username="ash", team_data="<html>test team</html>")
db.session.add_all([m, t])
db.session.commit()

# Test match and team, output: [<Match 1>] [<Team 1>]
Match.query.all()
Team.query.all()