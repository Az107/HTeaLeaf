import hashlib
import inspect
import json

from ..Elements import get_render_ctx
from ..JS import JSCode


class LocalState(JSCode):
    def __format__(self, format_spec: str, /) -> str:
        return "{{" + self.raw + "}}"


def use_state(init_state):
    frame = inspect.stack()[1]
    site = f"{frame.filename}:{frame.lineno}"
    raw = f"{site}:{json.dumps(init_state, sort_keys=True)}"
    id = hashlib.md5(raw.encode()).hexdigest()[:12]
    name = f"localstate_{id}"

    initializer = f'const {name} = new LocalState({json.dumps(init_state, sort_keys=True)},"{name}");'

    ctx = get_render_ctx()
    if ctx:
        ctx.register_state(initializer)

    return LocalState(name)
