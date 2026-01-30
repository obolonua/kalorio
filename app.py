from flask import (Flask,render_template, request, flash, redirect, url_for)
import sqlite3
import config
import users

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    username = request.form.get("username", "").strip()
    password1 = request.form.get("password1", "")
    password2 = request.form.get("password2", "")
    goal = request.form.get("daily_goal")

    if not username:
        flash("Kirjautumistunnus ei voi olla tyhjä.")
        return redirect(url_for("register"))

    if password1 != password2:
        flash("Salasanat eivät täsmää.")
        return redirect(url_for("register"))

    try:
        goal_value = int(goal) if goal else None
    except ValueError:
        flash("Päivittäisen tavoitteen täytyy olla numero.")
        return redirect(url_for("register"))

    try:
        users.create_user(username, password1, goal_value)
    except sqlite3.IntegrityError:
        flash("Käyttäjänimi on jo käytössä.")
        return redirect(url_for("register"))

    flash("Käyttäjä luotu. Kirjaudu sisään.")
    return redirect(url_for("login"))