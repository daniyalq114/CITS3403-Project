from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", active="home")

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # TODO: handle form
        return redirect(url_for("index"))
    return render_template("upload.html", active="upload")

# Stubbed routes so url_for() works
@app.route("/visualise")
def visualise():
    return render_template("visualise.html", active="visualise")

@app.route("/network")
def network():
    return render_template("network.html", active="network")

@app.route("/login")
def login():
    return render_template("login.html", active="login")

if __name__ == "__main__":
    app.run(debug=True)
