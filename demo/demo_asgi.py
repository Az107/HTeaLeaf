from htealeaf import adapters, HteaLeaf

from .components import init

app = HteaLeaf(adapters.ASGI)
init(app)
