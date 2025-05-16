from flask import render_template, request, redirect, url_for, flash, session, jsonify
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
    # need more form validation to make sure that links submitted are actually from 
    # pokemon showdown, so user can't craft malicious log files and SQL inject
    if request.method == "POST":
        # Read input from the form
        s_username = request.form.get("username", "").strip()
        user = User.query.filter_by(username=current_user.username).first()
        if current_user.showdown_username:
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
    replay_urls = session.get("replays", [])
    data_submitted = bool(replay_urls)

    def update_vis_session(name):
        parsed_logs = fetch_usr_matches_from_db(name)
        session["parsed_logs"] = parsed_logs
        session["active_match_id"] = parsed_logs[len(parsed_logs) - 1]["id"]

    if request.method == "POST": 
        target = request.form.get("username", "")
        if target and User.query.filter_by(showdown_username=target).first(): # update active logs to those of new user
            update_vis_session(target)
        elif not User.query.filter_by(showdown_username=target):
            flash(f"Whoops, looks like no replays have been submitted for user {target}!", "error")
    elif data_submitted: # data has just been submitted via upload page
        for replay_url in replay_urls:
            # Check if the replay URL already exists in the database
            existing_match = Match.query.filter_by(replay_url=replay_url).first()
            if existing_match:
                flash(f"Replay {replay_url} has already been processed.", "info")
                continue
            
            try: # parse log from url and add it to the database, and affiliate it with the current user
                parsed_log = ReplayLogParser(replay_url)
                save_parsed_log_to_db(parsed_log, db, current_user.showdown_username)
            except Exception as e:
                flash(f"Failed to process replay {replay_url}: {str(e)}", "error")
                continue
        # data_submitted will be false until more links are submitted in upload
        session.pop("replays", None) 
        update_vis_session(current_user.showdown_username)

    elif "parsed_logs" not in session and current_user.showdown_username:
        # no information parsed yet in this session, however the user
        # has submitted data before
        update_vis_session(current_user.showdown_username)

    #demorgans babyyy
    if not (data_submitted or current_user.showdown_username): 
        # user has not submitted and doesn't have a showdown_username
        return render_template("visualise.html", 
                            parsed_logs=[], 
                            data_submitted=False,
                            default_active_match_id=-1)
    else:
        return render_template("visualise.html", 
                                parsed_logs=session["parsed_logs"], 
                                data_submitted=True,
                                default_active_match_id=session["active_match_id"])

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
    session.clear()
    return redirect(url_for("main.index"))

@main.route("/visualise/match_data/<int:match_id>")
@login_required

def visualise_match_data(match_id):
    # Use the current user's showdown_username for security
    showdown_username = current_user.showdown_username
    data = fetch_pokemon_data_for_usr(showdown_username, match_id)
    print(data)
    return jsonify(data)
