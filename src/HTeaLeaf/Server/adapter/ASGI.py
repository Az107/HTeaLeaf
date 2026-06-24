from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Iterable, Literal, Optional

from HTeaLeaf.Server.adapter.adapter import adapter

from ..Http import Headers, Request, Response


@dataclass
class Scope:
    type: Literal["http"] | str
    asgi: dict[str, str]  # version and spec_version
    http_version: str
    method: str
    scheme: str
    path: str
    raw_path: bytes
    query_string: bytes
    root_path: str
    headers: Iterable[tuple[bytes, bytes]]
    client: tuple[str, int]
    server: tuple[str, Optional[int]]
    state: Optional[dict[str, Any]]


# dict struct
# recive event:
#     type: str
#     body: bytes
#     more_body: bool # if True wait for all the body chunks


def response_start(
    status: int, headers: Iterable[tuple[bytes, bytes]], trailers: bool
) -> dict[str, Any]:
    result = dict()
    result["type"] = "http.response.start"
    result["status"] = status
    result["headers"] = headers
    result["trailers"] = trailers
    return result


def response_body(body: bytes = b"", more_body=False) -> dict[str, Any]:
    result = dict()
    result["type"] = "http.response.body"
    result["body"] = body
    result["more_body"] = more_body
    return result


def headers_to_list(headers: Headers):
    header_list = []
    for k, v in headers:
        header_list.append((k.encode("utf-8"), v.encode("utf-8")))
    return header_list


@adapter
async def ASGI(
    handler: Callable[[Request], Awaitable[Response]],
    scope: dict,
    receive: Callable[[], Awaitable[dict]],
    send: Callable[[Any], Awaitable[None]],
):
    body: bytes = bytes()
    more = True
    while more:
        event = await receive()
        more = event["more_body"]
        body += event["body"]
    headers = [(k.decode(), v.decode()) for k, v in scope["headers"]]
    args_kv = scope["query_string"].decode().split("&") if scope["query_string"] else []
    args = {}
    for kv in args_kv:
        k, v = kv.split("=", 1)
        args[k] = v
    request = Request(scope["method"], path, args=args, headers=headers, body=body)

    response = await handler(request)
    body = (
        response.body.encode("utf-8")
        if isinstance(response.body, str)
        else response.body
    )

    await send(
        response_start(
            response.status.to_int(), iter(headers_to_list(response.headers)), False
        )
    )

    await send(response_body(body))
