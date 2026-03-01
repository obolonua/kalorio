from flask import (Flask, render_template, request, flash, redirect, url_for, session, abort)
import sqlite3
import re
from datetime import date, timedelta
import calendar
import entries
import functools
import secrets
import config
import users

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

MAX_DESCRIPTION_LENGTH = 50
CALORIES_PATTERN = re.compile(r"^[1-9]\d{0,3}$")

@app.before_request
def ensure_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(16)

def login_required(view):
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Kirjaudu sisään jatkaaksesi.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped

def check_csrf():
    if "csrf_token" not in session or session["csrf_token"] != request.form.get("csrf_token"):
        abort(403)

def is_description_valid(description):
    if not description:
        flash("Ruoka/kuvaus ei voi olla tyhjä.")
        return False
    if len(description) > MAX_DESCRIPTION_LENGTH:
        flash(f"Kuvauksen enimmäispituus on {MAX_DESCRIPTION_LENGTH} merkkiä.")
        return False
    return True

def is_calories_valid(calories):
    if not calories or not CALORIES_PATTERN.match(calories):
        flash("Kalorimäärän tulee olla 1-4 numeron positiivinen kokonaisluku (1-9999).")
        return False
    return True

def is_category_valid(category):
    if not entries.is_category_valid(category):
        flash("Aterian tulee olla Aamiainen, Lounas tai Illallinen.")
        return False
    return True

@app.route("/")
def index():
    published_food = entries.get_published_food(limit=20)
    return render_template("index.html", published_food=published_food)


@app.route("/users/<username>")
def user_profile(username):
    user = users.get_user_by_username(username)
    if not user:
        abort(404)
    published_food = entries.get_published_food_by_user(user["id"], limit=20)
    return render_template("user.html", user=user, published_food=published_food)


@app.route("/published/<int:published_id>")
def view_published_entry(published_id):
    entry = entries.get_published_entry(published_id)
    if not entry:
        abort(404)
    comments = entries.get_published_comments(published_id)
    return render_template(
        "published_entry.html",
        entry=entry,
        comments=comments,
    )


@app.route("/published/<int:published_id>/comment", methods=["POST"])
@login_required
def comment_published_entry(published_id):
    entry = entries.get_published_entry(published_id)
    if not entry:
        abort(404)

    check_csrf()

    comment_text = request.form.get("comment", "").strip()
    if not comment_text:
        flash("Kommentti ei voi olla tyhjä.")
        return redirect(url_for("view_published_entry", published_id=published_id))

    if entries.add_published_comment(published_id, session["user_id"], comment_text):
        flash("Kommentti tallennettu.")
    else:
        flash("Kommentin tallentaminen epäonnistui.")
    return redirect(url_for("view_published_entry", published_id=published_id))

@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    date_filter = request.args.get("entry_date") or date.today().isoformat()
    month_param = request.args.get("month")
    try:
        if month_param:
            year, month = [int(part) for part in month_param.split("-", 1)]
            month_date = date(year, month, 1)
        else:
            month_date = date.fromisoformat(date_filter).replace(day=1)
    except ValueError:
        month_date = date.today().replace(day=1)

    entry_list = entries.get_entries(
        user_id,
        entry_date=date_filter,
    )
    total = entries.get_daily_total(user_id, entry_date=date_filter)
    user = users.get_user(user_id)
    cal = calendar.Calendar(firstweekday=0)
    month_weeks = cal.monthdatescalendar(month_date.year, month_date.month)
    prev_month = (month_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month_year = month_date.year + (1 if month_date.month == 12 else 0)
    next_month_month = 1 if month_date.month == 12 else month_date.month + 1
    next_month = date(next_month_year, next_month_month, 1)
    return render_template(
        "dashboard.html",
        entries=entry_list,
        total=total,
        goal=user.get("daily_goal") if user else None,
        date_filter=date_filter,
        month_date=month_date,
        month_weeks=month_weeks,
        prev_month=prev_month,
        next_month=next_month,
    )

@app.route("/entries/new", methods=["GET", "POST"])
@login_required
def new_entry():
    if request.method == "GET":
        entry_date = request.args.get("entry_date") or date.today().isoformat()
        return render_template(
            "new_entry.html",
            categories=entries.get_category_choices(),
            selected_category=entries.DEFAULT_CATEGORY,
            entry_date=entry_date,
        )

    check_csrf()

    description = request.form.get("description", "").strip()
    calories = request.form.get("calories")
    entry_date = request.form.get("entry_date") or date.today().isoformat()
    category = request.form.get("category")

    if not is_description_valid(description):
        return redirect(url_for("new_entry"))

    if not is_calories_valid(calories):
        return redirect(url_for("new_entry"))

    if not is_category_valid(category):
        return redirect(url_for("new_entry"))

    calories_value = int(calories)
    entries.add_entry(
        session["user_id"],
        calories_value,
        description,
        entry_date,
        category,
    )
    flash("Merkintä tallennettu.")
    return redirect(url_for("dashboard", entry_date=entry_date))

@app.route("/entries/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    user_id = session["user_id"]
    entry = entries.get_entry(user_id, entry_id)
    if not entry:
        flash("Merkintää ei löytynyt.")
        return redirect(url_for("dashboard"))

    if request.method == "GET":
        return render_template(
            "edit_entry.html",
            entry=entry,
            categories=entries.get_category_choices(),
        )

    check_csrf()

    description = request.form.get("description", "").strip()
    calories = request.form.get("calories")
    category = request.form.get("category")

    if not is_description_valid(description):
        return redirect(url_for("edit_entry", entry_id=entry_id))

    if not is_calories_valid(calories):
        return redirect(url_for("edit_entry", entry_id=entry_id))

    calories_value = int(calories)
    if not is_category_valid(category):
        return redirect(url_for("edit_entry", entry_id=entry_id))

    if entries.update_entry(user_id, entry_id, description, calories_value, category):
        flash("Merkintä päivitetty.")
    else:
        flash("Merkintää ei löytynyt tai se ei kuulu sinulle.")
    return redirect(url_for("dashboard"))

@app.route("/entries/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_entry(entry_id):

    check_csrf()

    if entries.delete_entry(session["user_id"], entry_id):
        flash("Merkintä poistettu.")
    else:
        flash("Merkintää ei löytynyt tai se ei kuulu sinulle.")
    return redirect(url_for("dashboard"))


@app.route("/entries/<int:entry_id>/publish", methods=["POST"])
@login_required
def publish_entry(entry_id):
    check_csrf()
    if entries.publish_entry(session["user_id"], entry_id):
        flash("Merkintä julkaistu.")
    else:
        flash("Merkintää ei löytynyt tai se on jo julkaistu.")
    return redirect(url_for("dashboard"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    check_csrf()

    username = request.form.get("username", "").strip()
    password1 = request.form.get("password1", "")
    password2 = request.form.get("password2", "")
    goal = request.form.get("daily_goal")

    if not username:
        flash("Kirjautumistunnus ei voi olla tyhjä.")
        return redirect(url_for("register"))
    if len(username) < 6:
        flash("Kirjautumistunnuksen täytyy olla vähintään 6 merkkiä.")
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

    check_csrf()

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

@app.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session_keys = ["user_id", "username", "csrf_token"]
    for key in session_keys:
        session.pop(key, None)
    flash("Olet kirjautunut ulos.")
    return redirect(url_for("index"))