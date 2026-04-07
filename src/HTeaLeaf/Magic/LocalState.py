import hashlib
import inspect
import json

from ..Magic.jslib.JSCode import JSCode
from .RenderContext import get_render_ctx

# class localState():
#     def __init__(self, init_state):
#         self.do = JSDO("LocalState",init_state)

#     def

#     def js(self):
#         return self.do.js()

#     def get(self):
#         return self.do.get()

#     def set(self, data):
#         return self.do.set(data)


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

    return JSCode(name)
