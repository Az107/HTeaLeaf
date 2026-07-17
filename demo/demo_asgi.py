from htealeaf import HteaLeaf, adapters

from .components import init

app = HteaLeaf(adapters.ASGI)
init(app)
