from datetime import date

import db

CATEGORY_CHOICES = [
    ("breakfast", "Aamiainen"),
    ("lunch", "Lounas"),
    ("dinner", "Illallinen"),
]
CATEGORY_LABELS = {value: label for value, label in CATEGORY_CHOICES}
DEFAULT_CATEGORY = "lunch"


def _normalize_category(category):
    if category in CATEGORY_LABELS:
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
    entries = []
    for row in rows:
        entry = dict(row)
        entry["category_label"] = CATEGORY_LABELS.get(
            entry["category"], entry["category"]
        )
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
    entry["category_label"] = CATEGORY_LABELS.get(entry["category"], entry["category"])
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
    result = []
    for row in rows:
        entry = dict(row)
        entry["category_label"] = CATEGORY_LABELS.get(entry["category"], entry["category"])
        result.append(entry)
    return result

def delete_entry(user_id, entry_id):
    sql = """DELETE FROM entries
             WHERE id = ? AND user_id = ?"""
    cursor = db.execute(sql, [entry_id, user_id])
    return cursor.rowcount > 0