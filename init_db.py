import os
import sqlite3

from saver import save


if input("This will overwrite the existing db. Type 'I am sure' to continue: ") != "I am sure":
    quit()

import os
import sqlite3

schema_statements = [
    """CREATE TABLE pending_parents (
        num TEXT NOT NULL,
        parent TEXT NOT NULL,
        time INT NOT NULL,
        PRIMARY KEY (num, parent)
    )""",
    """CREATE TABLE queue (
        num TEXT NOT NULL PRIMARY KEY
    )""",
    """CREATE TABLE perfect (
        num TEXT NOT NULL PRIMARY KEY
    )""",
    """CREATE TABLE terminating (
        num TEXT NOT NULL PRIMARY KEY
    )""",
    """CREATE TABLE unknown (
        num TEXT NOT NULL PRIMARY KEY
    )""",
    """CREATE TABLE numbers (
        num TEXT NOT NULL PRIMARY KEY,
        next TEXT NOT NULL,
        code TEXT NOT NULL
    )""",
    """CREATE TABLE parents (
        num TEXT NOT NULL,
        parent TEXT NOT NULL,
        PRIMARY KEY (num, parent)
    )""",
    """CREATE TABLE times (
        num TEXT NOT NULL,
        parent TEXT NOT NULL,
        time INT NOT NULL,
        PRIMARY KEY (num, parent)
    )"""
]

# Remove the old database (if it exists)
try:
    os.remove("database.db")
except FileNotFoundError:
    pass


# Create a new connection and cursor
conn = sqlite3.connect("database.db")
cur = conn.cursor()

# Execute each CREATE TABLE statement separately
for statement in schema_statements:
    cur.execute(statement)


db = {"numbers": {1: {"next": 1, "code": "t", "parents": [], "times": {}}}, "unknown": [], "terminating": [1], "perfect": [], "queue": [], "pending_parents": {}}
save(db)

conn.commit()
conn.close()

print("DB reformatted.")
