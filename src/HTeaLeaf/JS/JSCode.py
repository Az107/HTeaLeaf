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
        if name == "raw":
            object.__setattr__(self, name, value)
        else:
            pass

    def __getattr__(self, name: str):
        return JSCode(f"{self.raw}.{name}")

    def __setitem__(self, key, value):
        return JSCode(f"{self.raw}[{key}] = {value}")

    def __delitem__(self, key):
        return JSCode(f"delete {self.raw}[{key}]")

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
        # from ..Store import AuthStore, Store

        parsed = []
        for arg in args:
            if isinstance(arg, JSCode):
                arg = arg.raw
            elif isinstance(arg, str):
                arg = json.dumps(arg)
            elif isinstance(arg, bool):
                arg = str(arg).lower()
            elif hasattr(arg, "_js"):
                arg = str(arg._js())
            else:
                arg = str(arg)

            parsed.append(arg)

        payload = ",".join(parsed)
        return JSCode(f"{self.raw}({payload})")

    def __call__(self, *args: Any):
        return self.call(*args)


class JSFunction:
    def __init__(self, name: str, raw: str):
        from ..State.RenderContext import get_render_ctx

        super().__init__()
        self.name = name
        self.raw = raw
        ctx = get_render_ctx()
        if ctx:
            ctx.register_state(raw)

    def __str__(self):
        return self.raw

    def __call__(self, *args):
        processed = []
        for arg in args:
            if isinstance(arg, JSCode):
                arg = arg
            elif hasattr(arg, "_js"):
                arg = arg._js
            processed.append(arg)
        return JSCode(f"{self.name}")(*processed)


FUNCTION_CACHE = {}


def js(fn: FunctionType):
    if fn.__code__ not in FUNCTION_CACHE:
        src = textwrap.dedent(inspect.getsource(fn))
        lines = src.splitlines()
        lines = [line for line in lines if not line.strip().startswith("@js")]
        src = "\n".join(lines)
        closure_vars = inspect.getclosurevars(fn)
        all_vars = {**fn.__globals__, **closure_vars.nonlocals, **closure_vars.globals}
        replace_map = get_jscode_ids(all_vars)
        FUNCTION_CACHE[fn.__code__] = transpile(src, replace_map)

    return JSFunction(fn.__name__, FUNCTION_CACHE[fn.__code__])


def get_jscode_ids(all_vars) -> dict[str, str]:
    name_map = {}
    for var_name, var_val in all_vars.items():
        # LocalState y Store exponen .js (JSCode), cuyo .raw es el identificador JS
        if hasattr(var_val, "raw"):
            name_map[var_name] = var_val.raw
        elif hasattr(var_val, "js"):
            name_map[var_name] = var_val.js.raw
    return name_map
