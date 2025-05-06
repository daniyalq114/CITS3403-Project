from flask import Flask, render_template, request, redirect, url_for, flash, session
from random import randint
import requests
from replay_parser import ReplayHTMLParser
from pokepaste_parser import PokePasteParser

app = Flask(__name__)
app.secret_key = "dev" # needed for flash messages    

@app.route("/")
def index():
    return render_template("index.html", active="home")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        #TODO: change this into database later
        # Read input from the form
        username = request.form.get("username", "").strip()
        pokepaste = request.form.get("pokepaste", "").strip()
        replays = [request.form.get(f"replay_{i}", "").strip() for i in range(40)]
        replays = [replay for replay in replays if replay]  # Filter out empty inputs

        # Store the data in the session
        session["username"] = username
        session["pokepaste"] = pokepaste
        session["replays"] = replays

        # Redirect to the visualise page
        return redirect(url_for("visualise"))

    return render_template("upload.html", active="upload")

@app.route("/visualise", methods=["GET", "POST"])
def visualise():
    username = session.get("username", "")
    pokepaste = session.get("pokepaste", "")
    replay_urls = session.get("replays", [])
    data_submitted = bool(replay_urls)
    games = []
    move_data = {}

    if data_submitted:
        # Parse PokéPaste data
        pokepaste_parser = PokePasteParser()
        pokemon_data = pokepaste_parser.parse_pokepaste(pokepaste)
        pokepaste_parser.populate_sprites()

        # Parse replays
        for replay_url in replay_urls:
            try:
                response = requests.get(replay_url)
                response.raise_for_status()
                parser = ReplayHTMLParser()
                parser.feed(response.text)

                # Get formatted game data
                game_data = parser.get_formatted_data(username)
                game_data["replay"]["search_request"] = replay_url
                games.append(game_data)

                # Update move data
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