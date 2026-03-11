import inspect
import json
import textwrap
from types import FunctionType
from typing import Any

from .py2js import transpile


class JSCode:
    def __init__(self, raw: str):
        self.raw = raw

    def __str__(self):
        return self.raw

    def __repr__(self):
        return self.raw

    def __invert__(self):
        return JSCode(f"!{self.raw}")

    def __setattr__(self, name: str, value: Any, /) -> None:
        pass

    def __getattr__(self, name: str):
        return JSCode(f"{self.raw}.{name}")

    def __add__(self, other):
        return JSCode(f"({self.raw} + {other})")

    def __sub__(self, other):
        return JSCode(f"({self.raw} - {other})")

    def __mul__(self, other):
        return JSCode(f"({self.raw} * {other})")

    def __truediv__(self, other):
        return JSCode(f"({self.raw} / {other})")

    def eq(self, other):
        return JSCode(f"({self.raw} == {other})")

    def ne(self, other):
        return JSCode(f"({self.raw} != {other})")

    def gt(self, other):
        return JSCode(f"({self.raw} > {other})")

    def lt(self, other):
        return JSCode(f"({self.raw} < {other})")


    def call(self, *args):
        from ..Store import AuthStore, Store
        parsed = []
        for arg in args:
            if isinstance(arg, JSCode):
                arg = str(arg)
            if isinstance(arg, str):
                arg = json.dumps(arg)
            if isinstance(arg, bool):
                arg = str(arg).lower()
            if isinstance(arg, Store) or isinstance(arg, AuthStore):
                arg = str(arg.do())

            parsed.append(arg)

        payload = ",".join(parsed)
        return JSCode(f"{self.raw}({payload})")


    def __call__(self, *args: Any):
        return self.call(*args)



class JSFunction():
    def __init__(self,name: str, raw: str):
        super().__init__()
        self.name = name
        self.raw = raw

    def __str__(self):
        return self.raw

    def __call__(self, *args):
        return JSCode(f"{self.name}")(*args)


def js(fn: FunctionType):
    src = textwrap.dedent(inspect.getsource(fn))
    lines = src.splitlines()
    lines = [l for l in lines if not l.strip().startswith("@js")]
    src = "\n".join(lines)
    return JSFunction(fn.__name__, transpile(src))
