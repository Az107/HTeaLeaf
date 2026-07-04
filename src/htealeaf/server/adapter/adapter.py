import functools
from typing import Callable, Awaitable
from ..http import Request, Response


def adapter(fn):
    def wrapper(handler: Callable[[Request], Awaitable[Response]]):
        application = functools.partial(fn, handler)
        return application
    return wrapper
