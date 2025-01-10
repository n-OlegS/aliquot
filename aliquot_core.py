import multiprocessing

from algs.pollardrho import rho_factorize
import json, random, time, logging

# default db:
# db = {"numbers": {1: {"next": 1, "code": "t", "parents": [], "times": {}}}, "unknown": [], "terminating": [1], "perfect": [], "queue": [], "pending_parents": {}}

# db = {"numbers": {1: {"next": 1, "code": "t", "parents": [], "times": {}}}, "unknown": [], "terminating": [1],
 #     "perfect": [], "queue": [2, 3, 4, 5, 6, 7, 8], "pending_parents": {}}


"""
SQL struct:
    pending_parents:
        key, value
    
    terminating
        key
        
    unknown
        key

    perfect
        key
        
    queue
        key
        
    numbers
        key, code, next, parents
        
    times
        key (number, from), value

Number times:
    -1 - fabricated

Return codes:
    0 - seq exist

Number codes:
    t - terminates
    p - perfect
    c - cycles
    l - leads to cycle
    L - leads to perfect
    u - unknown


Number object:
    KEY - n: 276
    next: 396
    code: u
    parents: []
    times: {parent: time} # -1 time means the calculation didn't happen (cached)


Main db object: {
    numbers: {}
    unknown: []
    terminating: []
    queue: []
    pending_parents: {number: parents}
"""


def next_number(db: dict, n):
    # get next number from cache, calculate and update if needed
    if n in db["numbers"]:
        return db["numbers"][n]["next"], -1

    need_update = False

    # if number is unknown

    start_t = int(time.time() * 1000)
    next_n = do_next_number(n)
    elapsed_t = int(time.time() * 1000) - start_t

    # clear from queues
    if n in db["unknown"]:
        db["unknown"].remove(n)
    if n in db["queue"]:
        db["queue"].remove(n)

    if n not in db["pending_parents"]:
        db["pending_parents"][n] = []

    # construct a new known number object
    n_obj = {"next": next_n, "code": "u", "parents": [x[0] for x in db["pending_parents"][n]], "times": {}}

    for i in db["pending_parents"][n]:
        n_obj["times"][i[0]] = i[1]

    # remove it from pending_parents
    del db["pending_parents"][n]

    if next_n in db["numbers"]:
        # reached an existing number
        # need to determine the code and update parents

        # update parents
        db["numbers"][next_n]["parents"].append(n)
        db["numbers"][next_n]["times"][n] = elapsed_t

        # determine code:
        next_code = db["numbers"][next_n]["code"]
        if next_code != "u":
            if next_code == "c":
                next_code = "l"
            elif next_code == "p":
                next_code = "P"

            need_update = True
    else:
        # reached a new number!
        # ensure n is a pending parent of next_n
        if next_n == n:
            n_obj["code"] = "p"
            db["perfect"].append(n)

            for parent in n_obj["parents"]:
                update_relatives(db, parent, "L")
        else:
            db["unknown"].append(next_n)

            if next_n in db["pending_parents"]:
                db["pending_parents"][next_n].append((n, elapsed_t))
            else:
                db["pending_parents"][next_n] = [(n, elapsed_t)]

    db["numbers"][n] = n_obj

    if need_update:
        update_relatives(db, n, next_code)

    return next_n, elapsed_t


def do_next_number(n):
    # calculate next
    return sum(rho_factorize(n)) - n


def update_relatives(db, n, code):
    # set code flag for N and all relatives
    to_update = [n]

    while len(to_update):
        current = to_update[0]
        to_update = to_update[1:]

        db["numbers"][current]["code"] = code

        if code == "t":
            db["terminating"].append(current)

        to_update += db["numbers"][current]["parents"].copy()

    if code == "t":
        db["terminating"] = list(set(db["terminating"]))


def assign_cycles():
    # assign cycles
    pass


def calculate_seq(n):
    # start the calculation from n until killed or terminated
    pass


def track(db, n, level=0):
    # see where the sequence terminated in the cache
    # this will also break later

    if n not in db["numbers"]:
        if level == 0:
            return -1
        else:
            return n
    elif db["numbers"][n]["code"] == "t":
        return 1
    elif db["numbers"][n]["code"] in ["p", "c"]:
        # this is sketchy because it gives a random element of a cycle and doesn't indicate the fact that a number is
        # perfect
        return n
    else:
        return track(db, db["numbers"][n]["next"], level=(level + 1))


def import_numbers(db, update_queue, l, queue=False):
    for n in l:
        if n in db["numbers"] or n in db["unknown"] or n in db["queue"]:
            continue

        if queue:
            db["queue"].append(n)
        else:
            db["unknown"].append(n)

    update_queue.put(db)

    # call a save function here

    # import numbers into queue or unknown


def ensure_seq(db, n, k):
    if k == 0:
        return
    # make sure the first k numbers of seq are known
    next_n = next_number(db, n)
    ensure_seq(db, next_n, k - 1)

    # this might give recursion errors later
