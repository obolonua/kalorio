from datetime import date

import db

def get_entries(user_id, limit=20, entry_date=None, keyword=None):
    clauses = ["user_id = ?"]
    params = [user_id]

    if entry_date:
        clauses.append("entry_date = ?")
        params.append(entry_date)

    if keyword:
        clauses.append("description LIKE ?")
        params.append(f"%{keyword}%")

    sql = f"""SELECT id, entry_date, description, calories
             FROM entries
             WHERE {" AND ".join(clauses)}
             ORDER BY entry_date DESC, id DESC
             LIMIT ?"""
    params.append(limit)
    rows = db.query(sql, params)
    return [dict(row) for row in rows]


def get_daily_total(user_id, entry_date=None):
    entry_date = entry_date or date.today().isoformat()
    sql = """SELECT SUM(calories) as total
             FROM entries
             WHERE user_id = ? AND entry_date = ?"""
    result = db.query(sql, [user_id, entry_date])
    if not result:
        return 0
    return result[0]["total"] or 0

def add_entry(user_id, calories, description, entry_date=None):
    entry_date = entry_date or date.today().isoformat()
    sql = """INSERT INTO entries (user_id, entry_date, description, calories)
             VALUES (?, ?, ?, ?)"""
    db.execute(sql, [user_id, entry_date, description, calories])

def update_entry(user_id, entry_id, description, calories):
    sql = """UPDATE entries
             SET description = ?, calories = ?
             WHERE id = ? AND user_id = ?"""
    cursor = db.execute(sql, [description, calories, entry_id, user_id])
    return cursor.rowcount > 0

def get_entry(user_id, entry_id):
    sql = """SELECT id, entry_date, description, calories
             FROM entries
             WHERE id = ? AND user_id = ?"""
    rows = db.query(sql, [entry_id, user_id])
    return dict(rows[0]) if rows else None