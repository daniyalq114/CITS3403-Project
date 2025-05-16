from flask_login import UserMixin
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from app import db  # Changed from 'config import db'

class User(UserMixin, db.Model):
    __tablename__ = "user"
    username = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    showdown_username = db.Column(db.String, unique=True,) 
    password = db.Column(db.String, nullable=False)
    matches = db.relationship("Match", back_populates="user", cascade="all, delete-orphan")  # Cascade delete
    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def get_id(self):
        return self.username  # Return username instead of id
    

class Match(db.Model):
    __tablename__ = "match"
    # add a date field too, so we can sort later
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    winner = db.Column(db.String)
    replay_url = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey("user.showdown_username"), nullable=False)  # Foreign key to User
    user = db.relationship("User", back_populates="matches")  # Back reference to User
    enemyname = db.Column(db.String)
    teams = db.relationship("Team", back_populates="match", cascade="all, delete-orphan")  # Cascade delete
    p1_initial_elo = db.Column(db.Integer)
    p1_final_elo = db.Column(db.Integer)
    p2_initial_elo = db.Column(db.Integer)
    p2_final_elo = db.Column(db.Integer)


class Team(db.Model):
    __tablename__ = "team"
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    match_id = db.Column(db.Integer, db.ForeignKey("match.id"), nullable=False)  # Foreign key to Match
    is_user_team = db.Column(db.Boolean, nullable=False)  # True = user's team, False = enemy's team
    match = db.relationship("Match", back_populates="teams")  # Back reference to Match
    pokemons = db.relationship("TeamPokemon", back_populates="team", cascade="all, delete-orphan")  # Cascade delete


class TeamPokemon(db.Model):
    __tablename__ = "team_pokemon"
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)  # Foreign key to Team
    pokemon_name = db.Column(db.String, nullable=False)  # Pokémon name
    ispick = db.Column(db.Boolean)
    wins = db.Column(db.Integer)
    defeated = db.Column(db.Boolean)
    # nickname = db.Column(db.String)  # Optional nickname
    # position = db.Column(db.Integer)  # Optional position (e.g., 1-6)
    team = db.relationship("Team", back_populates="pokemons")  # Back reference to Team
    move_usages = db.relationship("MoveUsage", back_populates="team_pokemon", cascade="all, delete-orphan")  # Cascade delete


class MoveUsage(db.Model):
    __tablename__ = "move_usage"
    id = db.Column(db.Integer, primary_key=True)  # Primary key
    team_pokemon_id = db.Column(db.Integer, db.ForeignKey("team_pokemon.id"), nullable=False)  # Foreign key to TeamPokemon
    move_name = db.Column(db.String, nullable=False)  # Move name
    times_used = db.Column(db.Integer, default=0)  # Number of times the move was used
    team_pokemon = db.relationship("TeamPokemon", back_populates="move_usages")  # Back reference to TeamPokemon
