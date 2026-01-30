import sqlite3
from flask import g

DB_PATH = "kalorio.db"


def get_connection():
    if "db" not in g:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_connection(error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def execute(sql, params=None):
    params = params or []
    connection = get_connection()
    cursor = connection.execute(sql, params)
    connection.commit()
    return cursor


def query(sql, params=None):
    params = params or []
    connection = get_connection()
    cursor = connection.execute(sql, params)
    return cursor.fetchall()