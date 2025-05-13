from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, Match, Team, TeamPokemon, MoveUsage
from app.blueprints import main
import requests
from app.replay_parser import *
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@main.route("/")
def index():
    username = session.get('user')
    return render_template("index.html", active="home", username=username)

@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # Read input from the form
        s_username = request.form.get("username", "").strip()
        if "user" not in session:
            flash("You must be logged in to upload data.", "danger")
            return redirect(url_for("main.login"))

        user = User.query.filter_by(username=session["user"]).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("main.login"))
        # best practice would be to authenticate with pokemon showdown
        if user.showdown_username:
            if user.showdown_username != s_username:
                flash(
                    f"Showdown username mismatch! Your current showdown username is '{user.showdown_username}'.",
                    "danger",
                )
                return redirect(url_for("main.upload"))
        else:
            user.showdown_username = s_username
            db.session.commit()
            flash("Showdown username updated successfully!", "success")
        # add a `replays` field to the session containing all of the replay links
        replays = [request.form.get(f"replay_{i}", "").strip() for i in range(40)]
        replays = [replay for replay in replays if replay]  # Filter out empty inputs
        session["replays"] = replays 

        # Redirect to the visualise page
        return redirect(url_for("main.visualise"))

    return render_template("upload.html", active="upload")


@main.route("/visualise", methods=["GET", "POST"])
@login_required
def visualise():
    # username = session.get("username", "")
    # pokepaste = session.get("pokepaste", "")
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

@main.route("/network", methods=["GET", "POST"])
@login_required
def network():
    users = [u.username for u in User.query.all()]
    if request.method == "POST":
        target = request.form.get("search_user", "")
        if not target:
            flash("Please enter a username to search.", "error")
            return redirect(url_for("main.network"))
        if target not in users:
            flash(f"User {target} not found.", "error")
            return redirect(url_for("main.network"))
        if target == current_user.username:
            flash("You cannot send a friend request to yourself.", "error")
            return redirect(url_for("main.network"))
        flash(f"Friend request sent to {target}", "success")
        return redirect(url_for("main.network"))
    return render_template("network.html", active="network", users=users)

@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("main.login"))
    return render_template("login.html", active="login")

@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]
        
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("main.signup"))
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return redirect(url_for("main.signup"))
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main.signup"))
            
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("signup.html", active="signup")

@main.route("/logout")
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("main.index"))
