from flask import (Flask,render_template,)

import config

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY


@app.route("/")
def index():
    return render_template("index.html")



