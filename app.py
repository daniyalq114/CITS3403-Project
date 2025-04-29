from flask import Flask, render_template, request, redirect, url_for, flash
from random import randint
import requests

app = Flask(__name__)
app.secret_key = "dev"  # needed for flash messages

@app.route("/")
def index():
    return render_template("index.html", active="home")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        username  = request.form.get("username", "")
        pokepaste = request.form.get("pokepaste", "")
        replays   = request.form.get("replays", "").splitlines()
        # TODO: process these values (e.g. save to DB, parse, etc.)
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
                "ELO":[], 
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
                "ELO":[], 
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
                "ELO":[], 
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
            mon["iconurl"] = jsondata["sprites"]["front_default"]  # Fetch the sprite URL
            
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
        # TODO: load real data for this username
        data_submitted = True

        # Example dummy data (you can remove when you have real stats)
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
    # Example users list; replace with real data source
    users = ["Ash", "Misty", "Brock", "May", "Dawn", "Gary"]

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
        # TODO: create a new user account
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", active="signup")

if __name__ == "__main__":
    app.run(debug=True)