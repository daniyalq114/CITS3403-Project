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

    shared_users = [
        s.owner_username
        for s in SharedAccess.query.filter_by(shared_with_username=current_user.username).all()
    ]

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

            elif shared_username in shared_users:
                session["shared_username"] = shared_username
                flash(f"You are viewing data shared by {shared_username}.", "success")
                update_vis_session(shared_username)

            else:
                flash("Invalid selection: You do not have access to this user's data.", "error")
                return redirect(url_for("main.visualise"))
            
        # update active logs to those of new user  
        if shared_username and User.query.filter_by(showdown_username=shared_username).first(): 
            update_vis_session(shared_username)

        elif not User.query.filter_by(showdown_username=shared_username):
            flash(f"Whoops, looks like no replays have been submitted for user {shared_username}!", "error")

    elif data_submitted: # data has just been submitted via upload page
        for replay_url in replay_urls:
            # Check if the replay URL already exists in the database
            existing_match = Match.query.filter_by(replay_url=replay_url).first()
            if existing_match:
                flash(f"Replay {replay_url} has already been processed.", "info")
                continue
            
            try: # parse log from url and add it to the database, and affiliate it with the current user
                parsed_log = ReplayLogParser(replay_url)
                save_parsed_log_to_db(parsed_log, db, current_user.username)
            except Exception as e:
                flash(f"Failed to process replay {replay_url}: {str(e)}", "error")
                continue
        # data_submitted will be false until more links are submitted in upload
        session.pop("replays", None) 
        update_vis_session(current_user.username)

    elif "parsed_logs" not in session and current_user.username:
        # no information parsed yet in this session, however the user
        # has submitted data before
        update_vis_session(current_user.username)

    #demorgans babyyy
    if not (data_submitted or current_user.username): 
        # user has not submitted and doesn't have a showdown_username
        return render_template("visualise.html", 
                            parsed_logs=[], 
                            data_submitted=False,
                            default_active_match_id=-1, 
                            shared_with=shared_users)
    else:
        return render_template("visualise.html", 
                                parsed_logs=session["parsed_logs"], 
                                data_submitted=True,
                                default_active_match_id=session["active_match_id"], 
                                shared_with=shared_users)

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
    # this is lowkey really gross 
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

# Additional endpoints 
@main.route("/logout")
def logout():
    logout_user()
    flash("Logged out.", "info")
    session.clear()
    return redirect(url_for("main.index"))

@main.route("/visualise/match_data/<int:match_id>")
@login_required
def visualise_match_data(match_id):
    # Use the current user's username for security
    username = current_user.username
    data = fetch_pokemon_data_for_usr(username, match_id)
    return jsonify(data)

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