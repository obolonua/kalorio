from datetime import date

import db

def get_entries(user_id, limit=20):
    sql = """SELECT id, entry_date, description, calories
             FROM entries
             WHERE user_id = ?
             ORDER BY entry_date DESC, id DESC
             LIMIT ?"""
    rows = db.query(sql, [user_id, limit])
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