from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable, Literal, Optional

from TeaLeaf.Server.Http.HttpHeader import Headers

from .Server import HttpRequest, Server


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





# dict struct
# recive event:
#     type: str
#     body: bytes
#     more_body: bool # if True wait for all the body chunks


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



def headers_to_list(headers: Headers):
    header_list = []
    for (k,v) in headers:
        header_list.append((k.encode("utf-8"), v.encode("utf-8")))
    return header_list


class ASGI(Server):
    def __init__(self):
        super().__init__()


    async def application(self,scope: dict,
                          receive: Callable[[], Awaitable[dict]],
                          send: Callable[[Any], Awaitable[None]]):
        body: bytes = bytes()
        more = True
        while more:
            event = await receive()
            more = event["more_body"]
            body += event["body"]
        headers = [(k.decode(), v.decode()) for k,v in scope["headers"]]
        request = HttpRequest(scope["method"],scope["path"],headers=headers,body=body)
        response = self.handle_request(request)
        body = response.body.encode("utf-8") if isinstance(response.body, str) else response.body

        await send(response_start(response.status.to_int(),iter(headers_to_list(response.headers)),False))

        await send(response_body(body))
