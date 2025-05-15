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
    if request.method == "POST":
        s_username = request.form.get("username", "").strip()
        user = current_user

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

        replays = [request.form.get(f"replay_{i}", "").strip() for i in range(40)]
        replays = [replay for replay in replays if replay]
        session["replays"] = replays

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

    # get users who shared with current user for search bar
    shared_users = [
        s.owner_username
        for s in SharedAccess.query.filter_by(shared_with_username=current_user.username).all()
    ]

    # handle shared user selection (POST request)
    if request.method == "POST":
        if request.form.get("clear_shared_user"):
            session.pop("shared_username", None)
            flash("You are viewing your own data.", "success")
            return redirect(url_for("main.visualise"))

        shared_username = request.form.get("shared_user")
        if shared_username:
            shared_username = shared_username.strip()

            if shared_username == current_user.username:
                session.pop("shared_username", None)
                flash("You are viewing your own data.", "success")
                return redirect(url_for("main.visualise"))

            elif shared_username in shared_users:
                session["shared_username"] = shared_username
                flash(f"You are viewing data shared by {shared_username}.", "success")
                return redirect(url_for("main.visualise"))
            else:
                flash("Invalid selection: You do not have access to this user's data.", "error")
                return redirect(url_for("main.visualise"))

    # determine which user's data to load (default to self)
    selected_user = session.get("shared_username", current_user.username)
    user = User.query.filter_by(username=selected_user).first()

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

    return render_template("visualise.html", active="visualise", shared_with=shared_users)


@main.route("/network", methods=["GET", "POST"])
@login_required
def network():
    if request.method == "POST" and request.is_json:
        target_username = request.json.get("username")

        if not target_username or target_username == current_user.username:
            return jsonify({'success': False, 'message': 'Invalid username'})

        user = User.query.filter_by(username=target_username).first()
        if not user:
            return jsonify({'success': False, 'message': 'User not found'})

        existing = SharedAccess.query.filter_by(
            owner_username=current_user.username,
            shared_with_username=target_username
        ).first()

        if existing:
            return jsonify({'success': False, 'message': 'Already shared with this user'})

        new_share = SharedAccess(
            owner_username=current_user.username,
            shared_with_username=target_username
        )
        db.session.add(new_share)
        db.session.commit()

        return jsonify({'success': True, 'message': f'Shared with {target_username}'})

    # GET request: render network.html with users and shared list
    all_users = [u.username for u in User.query.all() if u.username != current_user.username]
    already_shared = [s.shared_with_username for s in SharedAccess.query.filter_by(owner_username=current_user.username).all()]
    return render_template("network.html", users=all_users, shared_with=already_shared, active="network")



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

@main.route("/set_shared_user", methods=["POST"])
@login_required
def set_shared_user():
    data = request.get_json()
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"success": False, "message": "No user provided."})

    # Validate that the current user has access to this shared username
    access = SharedAccess.query.filter_by(
        owner_username=username,
        shared_with_username=current_user.username
    ).first()

    if access:
        session["shared_username"] = username
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "You do not have access to this user."})