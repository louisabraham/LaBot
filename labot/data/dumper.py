from threading import Lock
from functools import wraps
from pickle import dump


class WrappedMethod:
    def __init__(self, lock, method):
        @wraps(method)
        def locked_method(*args, **kwargs):
            with lock:
                return method(*args, **kwargs)

        self.locked_method = locked_method

    def __call__(self, *args, **kwargs):
        return self.locked_method(*args, **kwargs)


class Dumper:
    """
    Thread-safe dumping
    """

    def __init__(self, file: str):
        self.fd = open(file, mode="wb")
        self.lock = Lock()
        for method_name in dir(self.fd):
            if method_name.startswith("_"):
                continue
            method = getattr(self.fd, method_name)
            if not callable(method):
                continue

            setattr(self, method_name, WrappedMethod(self.lock, method))

    def dump(self, obj, protocol=None, *, fix_imports=True):
        return dump(obj, self, protocol, fix_imports)

    def __getattr__(self, attr):
        return getattr(self.socket, attr)
