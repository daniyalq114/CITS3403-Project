from app import db
from app.models import User, Match, Team, TeamPokemon, MoveUsage
from app.replay_parser import ReplayLogParser, save_parsed_log_to_db
from app.models import SharedAccess
from random import randint

def seed_data():
    linez = []
    with open("./static/samples/replay_links.txt") as f:
        linez = [line for line in f]
    
    usernms = ["Adam", "Daniyal", "Cam", "Sam"]
    for n in usernms:
        user = User(username=n)
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        # randomly add two lines for each individual
        for i in range(2):
            parsed_log = ReplayLogParser(linez.pop(randint(len(linez))))
            save_parsed_log_to_db(parsed_log, db, n)
            linez = set(linez)
            linez = list(linez)
        db.session.add_all([
            SharedAccess(owner_username="Adam", shared_with_username="Sam"),
            SharedAccess(owner_username="Daniyal", shared_with_username="Sam"),
            SharedAccess(owner_username="Cam", shared_with_username="Sam"),
        ])

    # Add more seed data as needed...