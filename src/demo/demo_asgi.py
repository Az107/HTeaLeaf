from components import init

from TeaLeaf.Server.ASGI import ASGI

app = ASGI()

init(app)


async def application(scope, receive, send):
    await app.application(scope, receive, send)
