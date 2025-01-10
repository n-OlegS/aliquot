import sqlite3


def save(orig_db: dict):
    db = orig_db.copy()

    con = sqlite3.connect('database.db')
    cur = con.cursor()

    tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    for table in tables:
        cur.execute(f"DELETE FROM {table[0]}")

    for n in db["unknown"]:
        cur.execute("INSERT INTO unknown (num) VALUES (?)", (str(n),))

    for n in db["terminating"]:
        cur.execute("INSERT INTO terminating (num) VALUES (?)", (str(n),))

    for n in db["perfect"]:
        cur.execute("INSERT INTO perfect (num) VALUES (?)", (str(n),))

    for n in db["queue"]:
        cur.execute("INSERT INTO queue (num) VALUES (?)", (str(n),))

    for key in db["pending_parents"]:
        for val in db["pending_parents"][key]:
            cur.execute(
                "INSERT INTO pending_parents (num, parent, time) VALUES (?, ?, ?)",
                (str(key), str(val[0]), val[1])
            )

    for n in db["numbers"]:
        next_n = db["numbers"][n]["next"]
        code = db["numbers"][n]["code"]
        cur.execute(
            "INSERT INTO numbers (num, next, code) VALUES (?, ?, ?)",
            (str(n), str(next_n), code)
        )

        for parent in db["numbers"][n]["parents"]:
            cur.execute(
                "INSERT INTO parents (num, parent) VALUES (?, ?)",
                (str(n), str(parent))
            )

        for parent in db["numbers"][n]["times"]:
            cur.execute(
                "INSERT INTO times (num, parent, time) VALUES (?, ?, ?)",
                (str(n), str(parent), db["numbers"][n]["times"][parent])
            )

    con.commit()
    con.close()


def load() -> dict:
    con = sqlite3.connect('database.db')
    cur = con.cursor()

    db = {
        "numbers": {},
        "unknown": [],
        "terminating": [],
        "perfect": [],
        "queue": [],
        "pending_parents": {}
    }

    # Load unknown numbers
    unknown_numbers = cur.execute("SELECT num FROM unknown").fetchall()
    db["unknown"] = [int(n[0]) for n in unknown_numbers]

    # Load terminating numbers
    terminating_numbers = cur.execute("SELECT num FROM terminating").fetchall()
    db["terminating"] = [int(n[0]) for n in terminating_numbers]

    # Load perfect numbers
    perfect_numbers = cur.execute("SELECT num FROM perfect").fetchall()
    db["perfect"] = [int(n[0]) for n in perfect_numbers]

    # Load queue numbers
    queue_numbers = cur.execute("SELECT num FROM queue").fetchall()
    db["queue"] = [int(n[0]) for n in queue_numbers]

    # Load pending parents
    pending_parents_rows = cur.execute("SELECT num, parent, time FROM pending_parents").fetchall()
    for num_str, parent_str, time in pending_parents_rows:
        num = int(num_str)
        parent = int(parent_str)
        if num not in db["pending_parents"]:
            db["pending_parents"][num] = []
        db["pending_parents"][num].append((parent, time))

    # Load numbers
    numbers_rows = cur.execute("SELECT num, next, code FROM numbers").fetchall()
    for num_str, next_str, code in numbers_rows:
        num = int(num_str)
        next_n = int(next_str)
        db["numbers"][num] = {
            "next": next_n,
            "code": code,
            "parents": [],
            "times": {}
        }

    # Load parents
    parents_rows = cur.execute("SELECT num, parent FROM parents").fetchall()
    for num_str, parent_str in parents_rows:
        num = int(num_str)
        parent = int(parent_str)
        if num in db["numbers"]:
            db["numbers"][num]["parents"].append(parent)
        else:
            db["numbers"][num] = {
                "next": None,
                "code": None,
                "parents": [parent],
                "times": {}
            }

    # Load times
    times_rows = cur.execute("SELECT num, parent, time FROM times").fetchall()
    for num_str, parent_str, time in times_rows:
        num = int(num_str)
        parent = int(parent_str)
        if num in db["numbers"]:
            db["numbers"][num]["times"][parent] = time
        else:
            db["numbers"][num] = {
                "next": None,
                "code": None,
                "parents": [],
                "times": {parent: time}
            }

    con.close()
    return db
