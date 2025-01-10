import random
import time
import multiprocessing
import threading

from aliquot_core import next_number, ensure_seq, track, do_next_number, import_numbers
from saver import save, load


def save_all(db):
    # implement saving logic
    save(dict(db))


def autosave_proc(db, interval=120):
    while 1:
        time.sleep(interval)
        save_all(db)


def main_task(db, queue, update_queue):
    # do queue
    # do random from unknown

    db = dict(db)

    queue.put(f"COMP: Main job started at {time.ctime()}")
    queue.put("COMP: Working from queue...")
    while len(db["queue"]):
        pending = db["queue"][0]
        queue.put(f"COMP: {time.ctime()} Working on number {pending}...")
        n, elapsed_t = next_number(db, pending)
        update_queue.put(db)
        queue.put(f"COMP: {time.ctime()} Processed {pending} in {elapsed_t}ms (result {n}).")

    queue.put(f"COMP: Queue complete! {time.ctime()}\nWorking from 'unknown' number base...")

    while len(db["unknown"]):
        pending = random.choice(db["unknown"])
        queue.put(f"COMP: {time.ctime()} Working on number {pending}...")
        n, elapsed_t = next_number(db, pending)
        update_queue.put(db)
        queue.put(f"COMP: {time.ctime()} Processed {pending} in {elapsed_t}ms (result {n}).")

    queue.put("COMP: Main job finished. This is unlikely to happen during normal operation.")


def get_seq(db, queue, update_queue, params):
    n, k = params
    db = dict(db)

    queue.put(f"COMP: Ensuring seq of {n}, {k}")

    ensure_seq(db, n, k - 1)

    update_queue.put(db)
    queue.put(f"COMP: Seq of {n}, {k} ensured.")

    seq = [n]

    # return the numbers

    for _ in range(k - 1):
        n = next_number(db, n)
        seq.append(n)

    assert len(seq) == k

    update_queue.put(db)
    queue.put("COMP: Finished.\n" + f"{seq}")


def computation_proc(db, out_queue, update_queue, task, params):
    if task == "main":
        main_task(db, out_queue, update_queue)
    elif task == "seq":
        get_seq(db, out_queue, update_queue, [int(x) for x in params])
    elif task == "track":
        result = track(dict(db), int(params[0]))

        if result == -1:
            out_queue.put(f"COMP: Track failed - {params[0]} not in base.")
        else:
            out_queue.put(f"COMP: Finished.\n{params[0]} tracks to {result}.")
    elif task == "next":
        db = dict(db)
        result = next_number(db, int(params[0]))[0]
        update_queue.put(db)
        out_queue.put(f"COMP: Finished.\nResult: {result}")
    elif task == "force":
        start_t = int(time.time() * 1000)
        result = do_next_number(int(params[0]))
        elapsed_t = int(time.time() * 1000) - start_t

        out_queue.put(f"COMP: Finished.\nNumber {params[0]} leads to {result} ({elapsed_t}ms).")
    elif task == "import":
        queue = True

        if params[0] == "-u":
            queue = False
            params = params[1:]

        params = [int(x) for x in params]

        import_numbers(dict(db), update_queue, params, queue=queue)
    else:
        raise ValueError


def output_queue_listener(queue):
    while True:
        try:
            message = queue.get()
            if message == "DONE":
                break

            print(message)
        except Exception as e:
            print(f"output_queue_listener exception:\n{e}")


def update_queue_listener(db, queue):
    while True:
        try:
            message = queue.get()
            if message == "DONE":
                break

            db.update(message)

        except Exception as e:
            print(f"update_queue_listener exception:\n{e}")


def interpreter(db):
    running_proc = multiprocessing.Process()
    output_queue = multiprocessing.Queue()
    update_queue = multiprocessing.Queue()

    current_code = ""

    listener_thread = threading.Thread(target=output_queue_listener, args=(output_queue,))
    updater_thread = threading.Thread(target=update_queue_listener, args=(db, update_queue))
    listener_thread.start()
    updater_thread.start()

    while 1:
        command = input("> ").split()

        if not command:
            continue

        args = command[1:]
        command = command[0]

        if command in ["s", "c", "stop", "cancel", "quit", "exit", "q"]:
            if running_proc.is_alive():
                running_proc.terminate()
                current_code = ""
                print("INT: Main process killed!")
            elif command not in ["quit", "exit", "q"]:
                print("INT: Main process is not running...")

            if command in ["quit", "exit", "q"]:
                save_all(db)
                output_queue.put("DONE")
                update_queue.put("DONE")
                listener_thread.join()
                updater_thread.join()
                return

        elif command in ["?"]:
            if current_code == "":
                output_queue.put("INT: No computation is currently running.")
            else:
                output_queue.put(f"INT: Currently running operation '{current_code}'")

        elif command in ["d"]:
            print(f"INT: Current db:\n{dict(db)}")

        elif command in ["save"]:
            save_all(db)
            print("INT: Saved!")
        elif command in ['help']:
            from texts import help_text
            print(help_text)
        elif command in ["docs"]:
            from texts import docs
            print(docs)
        else:
            if running_proc.is_alive():
                print("INT: The computational process is already running. Quit it before launching another computation.")
                continue

            launch_flag = True
            code = ""
            final_args = []

            if command in ["main", "m", "start"]:
                # start main proc
                code = "main"

            elif command in ["import", "i"]:
                code = "import"

                if len(args) == 0 or (args[0] == "-u" and len(args) == 1):
                    launch_flag = False
                    print("INT: Invalid args!")
                else:
                    final_args = args

            elif command in ["seq"]:
                # start seq
                code = "seq"

                if len(args) != 2:
                    launch_flag = False
                    print("INT: Invalid args!")
                else:
                    final_args = args

            elif command in ["track", "t"]:
                code = "track"

                if len(args) != 1:
                    launch_flag = False
                    print("INT: Invalid args!")
                else:
                    final_args = args

            elif command in ["next", "n"]:
                code = "next"

                if len(args) != 1:
                    launch_flag = False
                    print("INT: Invalid args!")
                else:
                    final_args = args

            elif command in ["force", "f"]:
                code = "force"

                if len(args) != 1:
                    launch_flag = False
                    print("INT: Invalid args!")
                else:
                    final_args = args

            else:
                print("INT: Unknown command...")
                launch_flag = False

            if launch_flag:
                running_proc = multiprocessing.Process(target=computation_proc, args=(db, output_queue, update_queue, code, final_args))
                running_proc.start()

                current_code = code


if __name__ == '__main__':
    manager = multiprocessing.Manager()
    shared_db = manager.dict()

    # orig_db = {"numbers": {1: {"next": 1, "code": "t", "parents": [], "times": {}}}, "unknown": [], "terminating": [1], "perfect": [], "queue": [276], "pending_parents": {}}
    orig_db = load()

    for key in list(orig_db.keys()):
        shared_db[key] = orig_db[key]

    autosaver = multiprocessing.Process(target=autosave_proc, args=(shared_db,))
    autosaver.start()

    interpreter(shared_db)
    autosaver.terminate()

