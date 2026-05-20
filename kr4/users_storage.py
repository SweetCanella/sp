from itertools import count
from threading import Lock

db: dict[int, dict] = {}

_id_seq = count(start=1)
_id_lock = Lock()


def next_user_id() -> int:
    with _id_lock:
        return next(_id_seq)


def clear_users():
    db.clear()
    global _id_seq
    _id_seq = count(start=1)
