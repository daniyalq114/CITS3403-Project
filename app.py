from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from random import randint
import random
import requests


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
    if app.debug:
        data_submitted = True
        usrmon = [
            {"name":"Reshiram", "moves":[["Giga Impact",], ["Light Screen",], ["Protect",], ["Reflect",]], "iconurl":""},
            {"name":"Darkrai", "moves":[["Dark Pulse",], ["Hyper Beam",], ["Throat Chop",], ["Thunder Wave",]], "iconurl":""}, 
            {"name":"Glalie", "moves":[["Avalanche",], ["Blizzard",], ["Body Slam",], ["Chilling Water",]], "iconurl":""}, 
            {"name":"Deoxys-Attack", "moves":[["Agility",], ["Brick Break",], ["Calm Mind",], ["Dark Pulse",]], "iconurl":""},
            {"name":"Regigigas", "moves":[["Giga Impact",], ["Hyper Beam",], ["Crush Grip",], ["Thunder",]], "iconurl":""},
            {"name":"Rayquaza", "moves":[["Giga Impact",], ["Draco Meteor",], ["Dragon Ascent",], ["Meteor Beam",]], "iconurl":""}]
        data = [
            {
                "win":True, 
                "enemyusr":{"name":"greg", "search_request":"google.com"},
                "replay":{"name":"replay", "search_request":"google.com"} ,
                "oppteam":["Rellor","Eiscue","Swablu","Aggron","Doduo","Applin"], 
                "usrpicks":[], 
                "opppicks":[], 
                "Terastallize":[],
                "ELO":[0]*3, 
                "OTS":True,
            },
            {
                "win":True, 
                "enemyusr":{"name":"ash ketchup", "search_request":"google.com"},
                "replay":{"name":"replay", "search_request":"google.com"}, 
                "oppteam":["Pancham","Jirachi","Luxio","Blissey","Toucannon","Pansage"],
                "usrpicks":[], 
                "opppicks":[], 
                "Terastallize":[],
                "ELO":[0]*3, 
                "OTS":True,
            },
            {
                "win":True, 
                "enemyusr":{"name":"obama", "search_request":"google.com"}, 
                "replay":{"name":"replay", "search_request":"google.com"},
                "oppteam":["Arbok","Klang","Kingdra","Machop","Panpour","Garchomp"],
                "usrpicks":[], 
                "opppicks":[], 
                "Terastallize":[],
                "ELO":[0]*3, 
                "OTS":True,
            }
        ]
        acc_elo = 1000
        # random entries
        for mon in usrmon:
            url = f"https://pokeapi.co/api/v2/pokemon/{mon['name'].lower()}/"
            response = requests.get(url)
            response.raise_for_status()
            jsondata = response.json()
            mon["iconurl"] = jsondata["sprites"]["front_default"]  
            
        for i in range(2, -1, -1):  # Fix range to include all indices
            temp = [pokemon["iconurl"] for pokemon in usrmon]  # Extract only the icon URLs
            data[i]["usrpicks"] = [temp.pop(randint(0, len(temp) - 1)) for _ in range(4)]
            # Populate oppteam with sprite URLs
            oppteam_sprites = []
            default_sprite = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png"
            for name in data[i]["oppteam"]:
                try:
                    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}/"
                    response = requests.get(url)
                    response.raise_for_status()
                    jsondata = response.json()
                    oppteam_sprites.append(jsondata["sprites"]["front_default"])
                except requests.exceptions.RequestException:
                    oppteam_sprites.append(default_sprite)
            data[i]["oppteam"] = oppteam_sprites
            temp = oppteam_sprites.copy()
            data[i]["opppicks"] = [temp.pop(randint(0, len(temp) - 1)) for _ in range(4)]
            # generate elo
            data[i]["ELO"][0] = acc_elo
            acc_elo += randint(10, 50)
            data[i]["ELO"][1] = acc_elo
            data[i]["ELO"][2] = randint(1000, 1200)
        username = ""
        labels = []
        values = []
        return render_template(
            "visualise.html",
            active="visualise",
            data_submitted=data_submitted,
            username=username,
            labels=labels,
            values=values, 
            games=data
        )
        
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
        # TODO: send friend request to target
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