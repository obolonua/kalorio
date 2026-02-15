from datetime import date
from functools import lru_cache

import db

DEFAULT_CATEGORY = "lunch"
FALLBACK_CATEGORIES = [(DEFAULT_CATEGORY, "Lounas")]
CATEGORY_QUERY = "SELECT value, label FROM meal_categories ORDER BY value"


@lru_cache(maxsize=1)
def _cached_category_data():
    rows = db.query(CATEGORY_QUERY)
    categories = [(row["value"], row["label"]) for row in rows]
    if not categories:
        categories = FALLBACK_CATEGORIES
    labels = {value: label for value, label in categories}
    return categories, labels


def get_category_choices():
    categories, _ = _cached_category_data()
    return categories


def _get_category_labels():
    _, labels = _cached_category_data()
    return labels


def _normalize_category(category):
    labels = _get_category_labels()
    if category in labels:
        return category
    return DEFAULT_CATEGORY


def get_entries(user_id, limit=20, entry_date=None, keyword=None):
    clauses = ["user_id = ?"]
    params = [user_id]

    if entry_date:
        clauses.append("entry_date = ?")
        params.append(entry_date)

    if keyword:
        clauses.append("description LIKE ?")
        params.append(f"%{keyword}%")

    sql = f"""SELECT id, entry_date, description, calories, category
             FROM entries
             WHERE {" AND ".join(clauses)}
             ORDER BY entry_date DESC, id DESC
             LIMIT ?"""
    params.append(limit)
    rows = db.query(sql, params)
    labels = _get_category_labels()
    entries = []
    for row in rows:
        entry = dict(row)
        entry["category_label"] = labels.get(entry["category"], entry["category"])
        entries.append(entry)
    return entries


def get_daily_total(user_id, entry_date=None):
    entry_date = entry_date or date.today().isoformat()
    sql = """SELECT SUM(calories) as total
             FROM entries
             WHERE user_id = ? AND entry_date = ?"""
    result = db.query(sql, [user_id, entry_date])
    if not result:
        return 0
    return result[0]["total"] or 0


def add_entry(user_id, calories, description, entry_date=None, category=None):
    entry_date = entry_date or date.today().isoformat()
    category = _normalize_category(category)
    sql = """INSERT INTO entries (user_id, entry_date, description, calories, category)
             VALUES (?, ?, ?, ?, ?)"""
    db.execute(sql, [user_id, entry_date, description, calories, category])


def update_entry(user_id, entry_id, description, calories, category=None):
    sql = """UPDATE entries
             SET description = ?, calories = ?, category = ?
             WHERE id = ? AND user_id = ?"""
    cursor = db.execute(
        sql,
        [description, calories, _normalize_category(category), entry_id, user_id],
    )
    return cursor.rowcount > 0


def get_entry(user_id, entry_id):
    sql = """SELECT id, entry_date, description, calories, category
             FROM entries
             WHERE id = ? AND user_id = ?"""
    rows = db.query(sql, [entry_id, user_id])
    if not rows:
        return None
    entry = dict(rows[0])
    entry["category_label"] = _get_category_labels().get(
        entry["category"], entry["category"]
    )
    return entry


def publish_entry(user_id, entry_id):
    entry = get_entry(user_id, entry_id)
    if not entry:
        return False

    sql = """INSERT OR IGNORE INTO published_food
             (entry_id, user_id, entry_date, description, calories, category)
             VALUES (?, ?, ?, ?, ?, ?)"""
    cursor = db.execute(
        sql,
        [
            entry_id,
            user_id,
            entry["entry_date"],
            entry["description"],
            entry["calories"],
            entry["category"],
        ],
    )
    return cursor.rowcount > 0


def get_published_food(limit=20):
    sql = """
    SELECT pf.id, pf.entry_date, pf.description, pf.calories, pf.category,
           pf.published_at, u.username
    FROM published_food pf
    JOIN users u ON pf.user_id = u.id
    ORDER BY pf.published_at DESC
    LIMIT ?
    """
    rows = db.query(sql, [limit])
    labels = _get_category_labels()
    result = []
    for row in rows:
        entry = dict(row)
        entry["category_label"] = labels.get(entry["category"], entry["category"])
        result.append(entry)
    return result


def get_published_entry(published_id):
    sql = """
    SELECT pf.id, pf.entry_id, pf.entry_date, pf.description, pf.calories,
           pf.category, pf.published_at, u.username
    FROM published_food pf
    JOIN users u ON pf.user_id = u.id
    WHERE pf.id = ?
    """
    rows = db.query(sql, [published_id])
    if not rows:
        return None
    entry = dict(rows[0])
    entry["category_label"] = _get_category_labels().get(entry["category"], entry["category"])
    return entry


def get_published_comments(published_id):
    sql = """
    SELECT pc.id, pc.body, pc.created_at, u.username
    FROM published_comments pc
    JOIN users u ON pc.user_id = u.id
    WHERE pc.published_id = ?
    ORDER BY pc.created_at ASC
    """
    rows = db.query(sql, [published_id])
    return [dict(row) for row in rows]


def add_published_comment(published_id, user_id, body):
    sql = """
    INSERT INTO published_comments (published_id, user_id, body)
    VALUES (?, ?, ?)
    """
    cursor = db.execute(sql, [published_id, user_id, body])
    return cursor.rowcount > 0


def delete_entry(user_id, entry_id):
    sql = """DELETE FROM entries
             WHERE id = ? AND user_id = ?"""
    cursor = db.execute(sql, [entry_id, user_id])
    return cursor.rowcount > 0