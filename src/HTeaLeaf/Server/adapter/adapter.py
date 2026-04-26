from types import FunctionType
import functools


def adapter(fn):
    def wrapper(handler: FunctionType):
        application = functools.partial(fn, handler)
        return application
    return wrapper
