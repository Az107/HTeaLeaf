from .Server import HttpRequest
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


def response_start(status: int, headers: Iterable[tuple[bytes,bytes]], trailers: bool) -> dict[str,Any]:
    result = dict()
    result["type"] = "http.response.start"
    result["status"] = status
    result["headers"] = headers
    result["trailers"] = trailers
    return result



def response_body(body: bytes = b"", more_body=False) -> dict[str,Any]:
    result = dict()
    result["type"] = "http.response.body"
    result["body"] = body
    result["more_body"] = more_body
    return result

class ASGI(Server):
    def __init__(self):
        super().__init__()


    async def application(self,scope: dict,
                          receive: Callable[[], Awaitable[dict]],
                          send: Callable[[dict], Awaitable[None]]):
        event = await receive()
        print(event)

        request = HttpRequest(scope["method"],scope["path"],headers=dict(),body=event["body"])
        status, headers, body = self.handle_request(request)
        await send(response_start(200,[],False))
        await send(response_body("".join(body).encode("utf-8")))
