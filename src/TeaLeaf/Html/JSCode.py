import json
from typing import Any


class JSCode:
    def __init__(self, raw: str):
        self.raw = raw

    def __str__(self):
        return self.raw

    def __repr__(self):
        return self.raw

    def __invert__(self):
        return JSCode(f"!{self.raw}")

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

    def call(self, *args):
        from ..Magic.Store import AuthStore, Store
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
            print(arg)
            parsed.append(arg)

        payload = ",".join(parsed)
        return JSCode(f"{self.raw}({payload})")


    def __call__(self, *args: Any):
        return self.call(*args)
