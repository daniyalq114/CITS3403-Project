from flask_login import UserMixin
from app import db

class User(UserMixin, db.Model):
    username = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    matches = db.relationship("Match", backref="user", lazy=True)
    teams = db.relationship("Team", backref="user", lazy=True)

    def get_id(self):
        return self.username  # Return username instead of id

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)
    match_id = db.Column(db.String, nullable=False)
    showdown_username = db.Column(db.String, nullable=False)
    match_info = db.Column(db.Text)

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey("user.username"), nullable=False)
    team_data = db.Column(db.Text)

# Association table for many-to-many relationship
pokemon_moves = db.Table('pokemon_moves',
    db.Column('pokemon_name', db.String, db.ForeignKey('pokemon.name'), primary_key=True),
    db.Column('move_name', db.String, db.ForeignKey('moves.name'), primary_key=True)
)

class Pokemon(db.Model):
    name = db.Column(db.String, primary_key=True)
    moves = db.relationship('Moves', secondary=pokemon_moves, backref='pokemon', lazy=True)

class Moves(db.Model):
    name = db.Column(db.String, primary_key=True)
    count = db.Column(db.Integer, nullable=False)
