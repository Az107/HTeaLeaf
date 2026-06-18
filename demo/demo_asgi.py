from HTeaLeaf import adapters, htealeaf

from .components import init

app = htealeaf(adapters.ASGI)
init(app)
