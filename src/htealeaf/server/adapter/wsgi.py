import asyncio
from typing import Any, Awaitable, Callable, Iterator

from htealeaf.error import ServerError

from ..http import Headers, Request, Response
from .adapter import adapter

# Cap the request body read so a large upload can't exhaust server memory.
MAX_BODY_SIZE = 10 * 1024 * 1024  # 10 MiB


def to_list(headers: Headers) -> list[tuple[str, str]]:
    return [h for h in headers]


@adapter
def WSGI(
    handler: Callable[[Request], Awaitable[Response]],
    environ: dict[str, Any],
    start_response,
) -> Iterator[bytes]:
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
    input_ = environ.get("wsgi.input")
    if input_ is None:
        body = None
    elif hasattr(input_, "read"):
        body = input_.read(MAX_BODY_SIZE + 1)
        if len(body) > MAX_BODY_SIZE:
            start_response("413 Payload Too Large", [("Content-Type", "text/plain")])
            return iter([b"Payload Too Large"])
    elif isinstance(input_, bytes):
        body = input_
    elif isinstance(input_, str):
        body = input_.encode()
    else:
        raise ServerError(f"[WSGI] Invalid body format: {type(input_)}")

    is_ssl = environ.get("wsgi.url_scheme") == "https"
    request = Request(
        method, path, headers=headers, body=body, body_handler=None, is_ssl=is_ssl
    )
    response = asyncio.run(handler(request))
    start_response(response.status.to_str(), to_list(response.headers))
    response_body: bytes = (
        response.body.encode("utf-8")
        if isinstance(response.body, str)
        else response.body
    )
    return iter([response_body])
