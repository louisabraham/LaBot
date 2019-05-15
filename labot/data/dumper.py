from threading import Lock
from functools import wraps
from pickle import dump


class Dumper:
    """
    Thread-safe dumping
    """

    def __init__(self, file: str):
        self.fd = open(file, mode="ab")
        self.lock = Lock()

    def write(self, b):
        with self.lock:
            self.fd.write(b)

    def dump(self, obj, protocol=None, *, fix_imports=True):
        return dump(obj, self, protocol, fix_imports=fix_imports)

    def __getattr__(self, attr):
        return getattr(self.fd, attr)
