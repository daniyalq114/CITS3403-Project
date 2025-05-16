# Import required Flask utilities and extensions
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db, login_manager
from app.models import User, Match, Team, TeamPokemon, MoveUsage
from app.blueprints import main
import requests
from app.replay_parser import *

# User session loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Home route - shows homepage
@main.route("/")
def index():
    username = session.get('user')
    return render_template("index.html", active="home", username=username)

# Upload page route - accepts replay URLs and showdown username
@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        # Extract Showdown username from form
        s_username = request.form.get("username", "").strip()

        # Ensure user is in session
        if "user" not in session:
            flash("You must be logged in to upload data.", "danger")
            return redirect(url_for("main.login"))

        # Validate user in database
        user = User.query.filter_by(username=session["user"]).first()
        if not user:
            flash("User not found.", "danger")
            return redirect(url_for("main.login"))

        # Check if Showdown username is already set
        if user.showdown_username:
            if user.showdown_username != s_username:
                flash(
                    f"Showdown username mismatch! Your current showdown username is '{user.showdown_username}'.",
                    "danger",
                )
                return redirect(url_for("main.upload"))
        else:
            # Save Showdown username if not already set
            user.showdown_username = s_username
            db.session.commit()
            flash("Showdown username updated successfully!", "success")

        # Extract and filter replay links from form
        replays = [request.form.get(f"replay_{i}", "").strip() for i in range(40)]
        replays = [replay for replay in replays if replay]
        session["replays"] = replays  # Store in session

        # Redirect to visualise page after successful upload
        return redirect(url_for("main.visualise"))

    # Display upload form if GET request
    return render_template("upload.html", active="upload")

# Visualise page route - processes and displays replay data
@main.route("/visualise", methods=["GET", "POST"])
@login_required
def visualise():
    replay_urls = session.get("replays", [])
    data_submitted = True  # Assume data has been submitted if user reached here
    games = []
    move_data = {}

    if data_submitted:
        # Process each replay link
        for replay_url in replay_urls:
            parsed_log = ReplayLogParser(replay_url)
            save_parsed_log_to_db(parsed_log, db)  # Save parsed data to DB

        # Render visualisation template
        return render_template("visualise.html")

# Network page route - allows searching and sending friend requests
@main.route("/network", methods=["GET", "POST"])
@login_required
def network():
    users = [u.username for u in User.query.all()]

    if request.method == "POST":
        target = request.form.get("search_user", "").strip()

        # Validate search input
        if not target:
            flash("Please enter a username to search.", "error")
            return redirect(url_for("main.network"))
        if target not in users:
            flash(f"User {target} not found.", "error")
            return redirect(url_for("main.network"))
        if target == current_user.username:
            flash("You cannot send a friend request to yourself.", "error")
            return redirect(url_for("main.network"))

        # Simulate friend request success
        flash(f"Friend request sent to {target}", "success")
        return redirect(url_for("main.network"))

    # Display network page with user list
    return render_template("network.html", active="network", users=users)

# Login page route - handles user authentication
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        # Validate user credentials
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!", "success")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("main.login"))

    # Display login form if GET request
    return render_template("login.html", active="login")

# Signup page route - handles new user registration
@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]

        # Validate unique username and email
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("main.signup"))
        if User.query.filter_by(email=email).first():
            flash("Email is already registered.", "danger")
            return redirect(url_for("main.signup"))
        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("main.signup"))

        # Register new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! You can now log in.", "success")
        return redirect(url_for("main.login"))

    # Display signup form if GET request
    return render_template("signup.html", active="signup")

# Logout route - logs out the user and redirects to homepage
@main.route("/logout")
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("main.index"))
