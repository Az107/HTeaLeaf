from HTeaLeaf.Server.adapter.ASGI import ASGI
from HTeaLeaf.Server.Server import Server

from .components import init

app = Server(ASGI)
init(app)


# async def application(scope, receive, send):
#     await app.application(scope, receive, send)
