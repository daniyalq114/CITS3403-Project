from flask import Flask, render_template, request, redirect, url_for



app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", active="home")

if __name__ == "__main__":
    app.run(debug=True)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        # TODO: parse form data, save to DB or session
        return redirect(url_for("visualise"))
    return render_template("upload.html", active="upload")

