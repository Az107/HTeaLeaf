from HTeaLeaf import HTeaLeaf, adapters

from .components import init

app = HTeaLeaf(adapters.ASGI)
init(app)
