CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    daily_goal INTEGER
);

CREATE TABLE entries (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_date TEXT NOT NULL,
    description TEXT,
    calories INTEGER NOT NULL CHECK (calories > 0),
    category TEXT NOT NULL DEFAULT 'lunch',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE published_food (
    id INTEGER PRIMARY KEY,
    entry_id INTEGER NOT NULL REFERENCES entries(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entry_date TEXT NOT NULL,
    description TEXT,
    calories INTEGER NOT NULL CHECK (calories > 0),
    category TEXT NOT NULL DEFAULT 'lunch',
    published_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(entry_id)
);
