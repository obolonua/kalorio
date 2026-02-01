from flask import (Flask,render_template, request, flash, redirect, url_for, session)
import sqlite3
import entries
import functools
import secrets
import config
import users

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Kirjaudu sisään jatkaaksesi.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    entry_list = entries.get_entries(user_id)
    total = entries.get_daily_total(user_id)
    user = users.get_user(user_id)
    return render_template("dashboard.html", entries=entry_list, total=total,
                           goal=user.get("daily_goal") if user else None)


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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    user_id = users.check_login(username, password)
    if not user_id:
        flash("Väärä tunnus tai salasana.")
        return redirect(url_for("login"))

    session["user_id"] = user_id
    session["username"] = username
    session["csrf_token"] = secrets.token_hex(16)
    flash("Tervetuloa takaisin!")
    return redirect(url_for("dashboard"))

@app.route("/logout")
def logout():
    session_keys = ["user_id", "username", "csrf_token"]
    for key in session_keys:
        session.pop(key, None)
    flash("Olet kirjautunut ulos.")
    return redirect(url_for("index"))