from flask import Flask, render_template, request, redirect, url_for, flash
import random

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
    data_submitted = False
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
        # TODO: create a new user account
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html", active="login")

if __name__ == "__main__":
    app.run(debug=True)
