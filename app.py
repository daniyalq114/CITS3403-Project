from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import random
import requests
from random import randint
import requests
from config import Config
from replay_parser import ReplayLogParser
app = Flask(__name__)
app.secret_key = "dev"  # Needed for flash messages
app.config.from_object(Config)
# --- Database setup ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import User, Match, Team, TeamPokemon, MoveUsage

# Routes
@app.route("/")
def index():
    return render_template("index.html", active="home")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # Read input from the form
        s_username = request.form.get("username", "").strip()
        if "user" not in session:
            flash("You must be logged in to upload data.", "danger")
            return redirect(url_for("login"))

        user = User.query.filter_by(username=session["user"]).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("login"))
        # best practice would be to authenticate with pokemon showdown
        if user.showdown_username:
            if user.showdown_username != s_username:
                flash(
                    f"Showdown username mismatch! Your current showdown username is '{user.showdown_username}'.",
                    "danger",
                )
                return redirect(url_for("upload"))
        else:
            user.showdown_username = s_username
            db.session.commit()
            flash("Showdown username updated successfully!", "success")

        pokepaste = request.form.get("pokepaste", "").strip()
        replays = [request.form.get(f"replay_{i}", "").strip() for i in range(40)]
        replays = [replay for replay in replays if replay]  # Filter out empty inputs

        # Store the data in the session
        # session["pokepaste"] = pokepaste
        session["replays"] = replays

        # Redirect to the visualise page
        return redirect(url_for("visualise"))

    return render_template("upload.html", active="upload")

@app.route("/visualise", methods=["GET", "POST"])
def visualise():
    # username = session.get("username", "")
    # pokepaste = session.get("pokepaste", "")
    print("swag")
    replay_urls = session.get("replays", [])
    # data_submitted = bool(replay_urls)
    data_submitted = True
    games = []
    move_data = {}

    if data_submitted:
        # # Parse PokéPaste data
        # pokepaste_parser = PokePasteParser()
        # pokemon_data = pokepaste_parser.parse_pokepaste(pokepaste)
        # pokepaste_parser.populate_sprites()
        # Parse replays
        # TODO prefil with None depending on the number of forms submitted
        for replay_url in replay_urls:
            # try:
                parsed_log = ReplayLogParser(replay_url)
                # writes relevant information to database
                save_parsed_log_to_db(parsed_log, db)
                
            # except Exception as e:
            #     flash(f"Failed to process replay {replay_url}: {str(e)}", "error")
            #     continue
        # games = [] 
        # fetch all matches associated with showdown user, and construct 'game' dicts to display
        # on Jinja
        # user = User.query.filter_by(username=session["user"]).first()
        # print(user.matches)
        return render_template("visualise.html")

    return render_template(
        "visualise.html",
        active="visualise",
        data_submitted=data_submitted,
        username=username,
        pokepaste=pokepaste,
        games=games,
        move_data=move_data,
        pokemon_data=pokemon_data if data_submitted else []
    )

@app.route("/network", methods=["GET", "POST"])
def network():
    users = [u.username for u in User.query.all()]
    if request.method == "POST":
        target = request.form.get("search_user", "")
        flash(f"Friend request sent to {target}", "success")
        return redirect(url_for("network"))
    return render_template("network.html", active="network", users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session["user"] = user.username
            flash("Logged in successfully!", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html", active="login")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("signup"))
        if User.query.filter_by(email=email).first():
            flash("Email already in use.", "danger")
            return redirect(url_for("signup"))
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", active="signup")

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out.", "info")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

def save_parsed_log_to_db(parsed_log, db):
    players = parsed_log.players
    match = Match(
        user_id=session["user"], # showdown name FK - links match to user
        # to store half as much data (when the opposing player submits their matches), have enemyname be another FK
        enemyname=players['p2'].name,
        teams=[]  # Teams will be added later
    )
    print("we get here")
    db.session.add(match)
    db.session.commit()

    # Add teams for the match
    for team_key in parsed_log.players.keys():
        team = Team(
            match_id=match.id,
            is_user_team=(team_key == 'p1')
        )
        db.session.add(team)
        db.session.commit()

        # Add Pokémon to the team
        for pokemon_name, pokemon_data in players[team_key].team.items():
            team_pokemon = TeamPokemon(
                team_id=team.id,
                pokemon_name=pokemon_name
            )
            db.session.add(team_pokemon)
            db.session.commit()

            # Add moves for the Pokémon
            for move_name, times_used in pokemon_data.moves.items():
                move_usage = MoveUsage(
                    team_pokemon_id=team_pokemon.id,
                    move_name=move_name,
                    times_used=times_used
                )
                db.session.add(move_usage)

    db.session.commit()

    # Update match winner and ELO data
    match.winner = parsed_log.winner
    for player_key, player in parsed_log.players.items():
        if player_key == "p1":
            match.p1_initial_elo = player.elo[0]
            match.p1_final_elo = player.elo[1]
        elif player_key == "p2":
            match.p2_initial_elo = player.elo[0]
            match.p2_final_elo = player.elo[1]
    db.session.commit()