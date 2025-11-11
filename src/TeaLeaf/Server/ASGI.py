from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Literal, Iterable, Optional
from .Server import Server


@dataclass
class Scope:
    type: Literal["http"] | str
    asgi: dict[str,str] #version and spec_version
    http_version: str
    method: str
    scheme: str
    path: str
    raw_path: bytes
    query_string: bytes
    root_path: str
    headers: Iterable[tuple[bytes, bytes]]
    client: tuple[str,int]
    server:  tuple[str, Optional[int]]
    state: Optional[dict[str,Any]]



@dataclass
class receiveEvent:
    type: str
    body: bytes
    more_body: bool # if True wait for all the body chunks

@dataclass
class sendEvent:
    type: str # http.response.start
    status: int
    headers: Iterable[tuple[bytes,bytes]]
    trailers: bool #


class ASGI(Server):

    async def application(self,scope: Scope, receive: Callable[[], Awaitable[receiveEvent]], send: Callable[[sendEvent], Awaitable[None]]):
        event = await receive()
        response = sendEvent("",0,[],False)
        await send(response)
