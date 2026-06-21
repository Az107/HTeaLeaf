from types import FunctionType
import functools
from typing import Callable, Awaitable
from ..Http import Request, Response


def adapter(fn):
    def wrapper(handler: Callable[[Request], Awaitable[Response]]):
        application = functools.partial(fn, handler)
        return application
    return wrapper
