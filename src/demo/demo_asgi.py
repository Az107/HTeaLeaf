from TeaLeaf.Server.ASGI import ASGI

from .components import init

app = ASGI()

init(app)


async def application(scope, receive, send):
    await app.application(scope, receive, send)
