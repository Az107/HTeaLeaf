from HTeaLeaf import adapters, HteaLeaf

from .components import init

app = HteaLeaf(adapters.ASGI)
init(app)
