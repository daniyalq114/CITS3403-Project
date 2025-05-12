from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import app, login_manager
from models import User, Match, Team, Pokemon, Moves, db
import requests

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/")
def index():
    username = session.get('user')
    return render_template("index.html", active="home", username=username)

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        pokepaste = request.form.get("pokepaste", "").strip()
        replays = [request.form.get(f"replay_{i}", "").strip() for i in range(40)]
        replays = [replay for replay in replays if replay]

        session["username"] = username
        session["pokepaste"] = pokepaste
        session["replays"] = replays

        return redirect(url_for("visualise"))

    return render_template("upload.html", active="upload")

@app.route("/visualise", methods=["GET", "POST"])
@login_required
def visualise():
    username = session.get("username", "")
    pokepaste = session.get("pokepaste", "")
    replay_urls = session.get("replays", [])
    data_submitted = bool(replay_urls)
    games = []
    move_data = {}

    if data_submitted:
        pokepaste_parser = PokePasteParser()
        pokemon_data = pokepaste_parser.parse_pokepaste(pokepaste)
        pokepaste_parser.populate_sprites()

        for replay_url in replay_urls:
            try:
                response = requests.get(replay_url)
                response.raise_for_status()
                parser = ReplayHTMLParser()
                parser.feed(response.text)

                game_data = parser.get_formatted_data(username)
                game_data["replay"]["search_request"] = replay_url
                games.append(game_data)

                for pokemon, moves in parser.move_usage.items():
                    if pokemon not in move_data:
                        move_data[pokemon] = {}
                    for move, count in moves.items():
                        if move not in move_data[pokemon]:
                            move_data[pokemon][move] = 0
                        move_data[pokemon][move] += count

            except Exception as e:
                flash(f"Failed to process replay {replay_url}: {str(e)}", "error")
                continue

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
@login_required
def network():
    users = [u.username for u in User.query.all()]
    if request.method == "POST":
        target = request.form.get("search_user", "")
        if not target:
            flash("Please enter a username to search.", "warning")
            return redirect(url_for("network"))
        if target not in users:
            flash(f"User {target} not found.", "error")
            return redirect(url_for("network"))
        flash(f"Friend request sent to {target}", "success")
        return redirect(url_for("network"))
    return render_template("network.html", active="network", users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
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
        confirm_password = request.form["confirm-password"]
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("signup"))
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return redirect(url_for("signup"))
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", active="signup")

@app.route("/logout")
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("index"))