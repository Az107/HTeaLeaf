# thread-local render context
import threading

# from ...Server.Server import Server, ServerEvent
from ..Elements import Component, script

_render_ctx = threading.local()


class RenderContext:
    def __init__(self):
        self.js_functions = []  # JSFunction objects
        self.state_initializers = []  # LocalStateInitializer objects

    def register_js(self, fn):
        if fn not in self.js_functions:
            self.js_functions.append(fn)

    def register_state(self, initializer):

        if initializer not in self.state_initializers:
            self.state_initializers.append(initializer)


def _inject_context(node: Component):
    ctx = get_render_ctx()
    if ctx is None:
        return

    scripts = [script(fn) for fn in ctx.js_functions] + [
        script(fn) for fn in ctx.state_initializers
    ]
    if not scripts:
        return

    # BFS search head node
    queue = [node]
    while queue:
        current = queue.pop(0)
        if current.name == "head":
            for s in reversed(scripts):
                current.prepend(s)
            return
        for child in current.children:
            if isinstance(child, Component):
                queue.append(child)

    # Fallback: inyect at root
    for s in reversed(scripts):
        node.prepend(s)


def get_render_ctx() -> RenderContext | None:
    return getattr(_render_ctx, "current", None)


def init_render_ctx():
    _render_ctx.current = RenderContext()


# def enable_render_context(server: "Server"):

#     def _on_request_hook(*args):
#         _render_ctx.current = RenderContext()

#     def _on_render_hook(component: Component):
#         ctx = get_render_ctx()
#         if ctx:
#             _inject_context(component)
#             _render_ctx.current = None

# server.registry_hook(ServerEvent.on_request, _on_request_hook)
# server.registry_hook(ServerEvent.on_render, _on_render_hook)
