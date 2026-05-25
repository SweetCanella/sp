from itertools import count
from threading import Lock


class TaskStorage:
    """Простое хранилище задач в памяти."""

    def __init__(self):
        self.tasks: dict[int, dict] = {}
        self._id_seq = count(start=1)
        self._lock = Lock()

    def next_id(self) -> int:
        with self._lock:
            return next(self._id_seq)

    def clear(self):
        self.tasks.clear()
        self._id_seq = count(start=1)


storage = TaskStorage()


def get_storage() -> TaskStorage:
    return storage
