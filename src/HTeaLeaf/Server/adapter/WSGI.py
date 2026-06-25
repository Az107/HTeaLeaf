import asyncio
from types import FunctionType
from typing import Iterator, Callable, Awaitable

from HTeaLeaf.Server.adapter.adapter import adapter

from ..Http import Headers, Request, Response


def to_list(headers: Headers) -> list[tuple[str, str]]:
    return [h for h in headers]

@adapter
def WSGI(handler: Callable[[Request], Awaitable[Response]],environ: dict[str, str], start_response) -> Iterator[bytes]:
    path = environ.get("PATH_INFO", "/")
    method = environ.get("REQUEST_METHOD", "GET")
    headers = {}
    try:
        headers["content_length"] = int(environ.get("CONTENT_LENGTH", 0))
    except ValueError:
        headers["content_length"] = 0
    for k in environ:
        if k.startswith("HTTP_"):
            headers[k[5:]] = environ[k]
    body = environ.get("wsgi.input", "body").encode()
    request = Request(method, path, headers=headers, body=body)
    response = asyncio.run(handler(request))
    start_response(response.status.to_str(), to_list(response.headers))
    response_body: bytes = (
        response.body.encode("utf-8")
        if isinstance(response.body, str)
        else response.body
    )
    return iter([response_body])
