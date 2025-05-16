# Standard Flask and Flask-Login imports
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user

# App-specific imports
from app import db, login_manager
from app.models import User, Match, Team, TeamPokemon, MoveUsage, SharedAccess
from app.blueprints import main
from app.replay_parser import *

import requests

# --------------------------
# Flask-Login user loader
# --------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# --------------------------
# Home Page
# --------------------------
@main.route("/")
def index():
    # Retrieve logged-in username from session if available
    username = session.get('user')
    return render_template("index.html", active="home", username=username)


# --------------------------
# Upload Replay Links
# --------------------------
@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    # NOTE: Input validation should be improved to ensure replay URLs are legitimate Showdown logs
    if request.method == "POST":
        s_username = request.form.get("username", "").strip()
        user = current_user

        # Validate or set showdown username
        if user.showdown_username:
            if user.showdown_username != s_username:
                flash(f"Showdown username mismatch! Your current showdown username is '{user.showdown_username}'.", "danger")
                return redirect(url_for("main.upload"))
        else:
            user.showdown_username = s_username
            db.session.commit()
            flash("Showdown username updated successfully!", "success")

        # Collect and filter replay links (up to 40)
        replays = [request.form.get(f"replay_{i}", "").strip() for i in range(40)]
        replays = [r for r in replays if r]
        session["replays"] = replays

        # Proceed to visualisation
        return redirect(url_for("main.visualise"))

    return render_template("upload.html", active="upload")


# --------------------------
# Visualise Processed Replays
# --------------------------
@main.route("/visualise", methods=["GET", "POST"])
@login_required
def visualise():
    replay_urls = session.get("replays", [])
    data_submitted = bool(replay_urls)

    # Updates session with user's parsed match logs
    def update_vis_session(name):
        parsed_logs = fetch_usr_matches_from_db(name)
        session["parsed_logs"] = parsed_logs
        session["active_match_id"] = parsed_logs[-1]["id"]

    # Get all users who have shared their data with the current user
    shared_users = [s.owner_username for s in SharedAccess.query.filter_by(shared_with_username=current_user.username).all()]

    if request.method == "POST":
        # Clear shared user selection
        if request.form.get("clear_shared_user"):
            session.pop("shared_username", None)
            flash("You are viewing your own data.", "success")
            update_vis_session(current_user.username)
            return redirect(url_for("main.visualise"))

        # Switch to a shared user's data if allowed
        shared_username = request.form.get("shared_user", "").strip()
        if shared_username:
            if shared_username == current_user.username:
                session.pop("shared_username", None)
                flash("You are viewing your own data.", "success")
                update_vis_session(current_user.username)
            elif shared_username in shared_users:
                session["shared_username"] = shared_username
                flash(f"You are viewing data shared by {shared_username}.", "success")
                update_vis_session(shared_username)
            else:
                flash("Invalid selection: You do not have access to this user's data.", "error")
                return redirect(url_for("main.visualise"))

    # Process uploaded replays if available
    elif data_submitted:
        for replay_url in replay_urls:
            if Match.query.filter_by(replay_url=replay_url).first():
                flash(f"Replay {replay_url} has already been processed.", "info")
                continue

            try:
                parsed_log = ReplayLogParser(replay_url)
                save_parsed_log_to_db(parsed_log, db, current_user.username)
            except Exception as e:
                flash(f"Failed to process replay {replay_url}: {str(e)}", "error")
                continue

        session.pop("replays", None)
        update_vis_session(current_user.username)

    # Load existing data if user has history but no new submissions this session
    elif "parsed_logs" not in session and current_user.showdown_username:
        update_vis_session(current_user.username)

    # If no data, show empty visualisation
    if not (data_submitted or current_user.showdown_username):
        return render_template("visualise.html", parsed_logs=[], data_submitted=False, default_active_match_id=-1, shared_with=shared_users)

    # Render visualisation with available data
    return render_template("visualise.html", parsed_logs=session["parsed_logs"], data_submitted=True, default_active_match_id=session["active_match_id"], shared_with=shared_users)


# --------------------------
# Network - Share Data with Other Users
# --------------------------
@main.route("/network", methods=["GET", "POST"])
@login_required
def network():
    if request.method == "POST" and request.is_json:
        target_username = request.json.get("username")

        # Validate target user
        if not target_username or target_username == current_user.username:
            return jsonify({'success': False, 'message': 'Invalid username'})

        user = User.query.filter_by(username=target_username).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})

        # Prevent duplicate sharing
        existing = SharedAccess.query.filter_by(owner_username=current_user.username, shared_with_username=target_username).first()
        if existing:
            return jsonify({'success': False, 'message': 'Already shared with this user'})

        # Add sharing record
        new_share = SharedAccess(owner_username=current_user.username, shared_with_username=target_username)
        db.session.add(new_share)
        db.session.commit()

        return jsonify({'success': True, 'message': f'Shared with {target_username}'})

    # Render network management page
    all_users = [u.username for u in User.query.all() if u.username != current_user.username]
    already_shared = [s.shared_with_username for s in SharedAccess.query.filter_by(owner_username=current_user.username).all()]
    return render_template("network.html", users=all_users, shared_with=already_shared, active="network")


# --------------------------
# Login Page
# --------------------------
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        # Validate credentials
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("main.index"))
        else:
            flash("Invalid username or password.", "danger")
            return redirect(url_for("main.login"))

    return render_template("login.html", active="login")


# --------------------------
# Signup Page
# --------------------------
@main.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm-password"]

        # Validate username, email, and password
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

    return render_template("signup.html", active="signup")


# --------------------------
# Logout User
# --------------------------
@main.route("/logout")
def logout():
    logout_user()
    flash("Logged out.", "info")
    session.clear()  # Clear session data
    return redirect(url_for("main.index"))


# --------------------------
# Fetch Match Data for Visualisation (AJAX)
# --------------------------
@main.route("/visualise/match_data/<int:match_id>")
@login_required
def visualise_match_data(match_id):
    username = current_user.username  # Ensure data belongs to logged-in user
    data = fetch_pokemon_data_for_usr(username, match_id)
    return jsonify(data)


# --------------------------
# Set Shared User Context (AJAX)
# --------------------------
@main.route("/set_shared_user", methods=["POST"])
@login_required
def set_shared_user():
    data = request.get_json()
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"success": False, "message": "No user provided."})

    # Verify access to shared user data
    access = SharedAccess.query.filter_by(owner_username=username, shared_with_username=current_user.username).first()
    if access:
        session["shared_username"] = username
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "You do not have access to this user."})
