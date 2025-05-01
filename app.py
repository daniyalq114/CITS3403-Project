from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import random

app = Flask(__name__)
app.secret_key = "dev"  # Needed for flash messages
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# --- Database setup ---
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- Models ---
class User(db.Model):
    username = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    matches = db.relationship("Match", backref="user", lazy=True)
    teams = db.relationship("Team", backref="user", lazy=True)

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

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html", active="home")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        username = request.form.get("username", "")
        pokepaste = request.form.get("pokepaste", "")
        replays = request.form.get("replays", "").splitlines()

        # TODO: Save to database (e.g., User, Team, Match)
        flash("Upload received!", "success")
        return redirect(url_for("index"))
    return render_template("upload.html", active="upload")

@app.route("/visualise", methods=["GET", "POST"])
def visualise():
    data_submitted = False
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        data_submitted = True

        # TODO: Load actual match data from DB
        labels = ["Win", "Loss", "Draw"]
        values = [random.randint(1, 10) for _ in labels]
    else:
        labels = []
        values = []

    return render_template(
        "visualise.html",
        active="visualise",
        data_submitted=data_submitted,
        username=username,
        labels=labels,
        values=values
    )

@app.route("/network", methods=["GET", "POST"])
def network():
    users = ["Ash", "Misty", "Brock", "May", "Dawn", "Gary"]  # TODO: Replace with User.query.all()

    if request.method == "POST":
        target = request.form.get("search_user", "")
        # TODO: send friend request to `target`
        flash(f"Friend request sent to {target}", "success")
        return redirect(url_for("network"))

    return render_template("network.html", active="network", users=users)

@app.route("/login", methods=["GET", "POST"])
def login():
    # stub for future implementation
    return render_template("login.html", active="login")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # TODO: Save new user to DB
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", active="signup")

if __name__ == "__main__":
    app.run(debug=True)
