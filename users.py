from werkzeug.security import check_password_hash, generate_password_hash

import db


def create_user(username, password, goal=None):
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash, daily_goal) VALUES (?, ?, ?)"
    db.execute(sql, [username, password_hash, goal])

def check_login(username, password):
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    record = result[0]
    if check_password_hash(record["password_hash"], password):
        return record["id"]
    return None

def get_user(user_id):
    sql = "SELECT id, username, daily_goal FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return dict(result[0]) if result else None